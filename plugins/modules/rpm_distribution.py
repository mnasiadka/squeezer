#!/usr/bin/python


# copyright (c) 2020, Jacob Floyd
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rpm_distribution
short_description: Manage rpm distributions of a pulp api server instance
description:
  - "This performs CRUD operations on rpm distributions in a pulp api server instance."
options:
  name:
    description:
      - Name of the distribution to query or manipulate
    type: str
    required: false
  base_path:
    description:
      - Base path to distribute a publication
    type: str
    required: false
  publication:
    description:
      - Href of the publication to be served
    type: str
    required: false
  repository:
    description:
      - Name of the repository to be served
    type: str
    required: false
    version_added: "0.0.15"
  content_guard:
    description:
      - Name of the content guard for the served content
      - "Warning: This feature is not yet supported."
    type: str
    required: false
extends_documentation_fragment:
  - pulp.squeezer.pulp
  - pulp.squeezer.pulp.entity_state
author:
  - Jacob Floyd (@cognifloyd)
"""

EXAMPLES = r"""
- name: Read list of rpm distributions
  pulp.squeezer.rpm_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: distribution_status
- name: Report pulp rpm distributions
  debug:
    var: distribution_status

- name: Create a rpm distribution
  pulp.squeezer.rpm_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_rpm_distribution
    base_path: new/rpm/dist
    publication: /pub/api/v3/publications/rpm/rpm/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/
    state: present

- name: Delete a rpm distribution
  pulp.squeezer.rpm_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_rpm_distribution
    state: absent
"""

RETURN = r"""
  distributions:
    description: List of rpm distributions
    type: list
    returned: when no name is given
  distribution:
    description: Rpm distribution details
    type: dict
    returned: when name is given
"""


from ansible_collections.pulp.squeezer.plugins.module_utils.pulp import (
    PulpContentGuard,
    PulpEntityAnsibleModule,
    PulpRpmDistribution,
    PulpRpmRepository,
)


def main():
    with PulpEntityAnsibleModule(
        argument_spec=dict(
            name=dict(),
            base_path=dict(),
            publication=dict(),
            repository=dict(),
            content_guard=dict(),
        ),
        required_if=[
            ("state", "present", ["name", "base_path"]),
            ("state", "absent", ["name"]),
        ],
        mutually_exclusive=[("publication", "repository")],
    ) as module:
        content_guard_name = module.params["content_guard"]
        repository_name = module.params["repository"]

        natural_key = {"name": module.params["name"]}
        desired_attributes = {
            key: module.params[key]
            for key in ["base_path", "publication", "repository"]
            if module.params[key] is not None
        }

        # support switching between using publication and repository
        if module.params["publication"] is not None:
            desired_attributes["repository"] = None
        elif repository_name is not None:
            desired_attributes["publication"] = None
            repository = PulpRpmRepository(module, {"name": repository_name})
            repository.find(failsafe=False)
            desired_attributes["repository"] = repository.href

        if content_guard_name is not None:
            if content_guard_name:
                content_guard = PulpContentGuard(module, {"name": content_guard_name})
                content_guard.find(failsafe=False)
                desired_attributes["content_guard"] = content_guard.href
            else:
                desired_attributes["content_guard"] = None

        PulpRpmDistribution(module, natural_key, desired_attributes).process()


if __name__ == "__main__":
    main()
