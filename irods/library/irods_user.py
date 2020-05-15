#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Provides an ansible module for creating, updating and removing iRODS users.
"""

import ssl
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community"
}

DOCUMENTATION = """
---
module: irods_user

short_description: Create/Update/Remove iRODS user

version_added: "2.4"

description:
    - Create iRODS user.
    - Update iRODS user's type or password.
    - Remove iRODS user.

options:
    name:
        description:
            - Username of user
        required: true
        type: str
    state:
        description:
            - Desired state to achieve
            - Either present or absent
        required: true
        choices:
            - present
            - absent
        type: str
    type:
        description:
            - User's type
            - Only meaningful when state is 'present'
            - Type to change into if user exist with a different type
        required: false
        default: rodsuser
        type: str
    password:
        description:
            - User's password
            - Only meaningful when state is 'present'
        required: false
        type: str
    host:
        description:
            - Hostname of the iRODS server
        required: true
        type: str
    port:
        description:
            - Port of the iRODS server
        required: true
        type: int
    admin_user:
        description:
            - Username of the admin user
        required: true
        type: str
    admin_password:
        description:
            - Password of the admin user
        required: true
        type: str
    zone:
        description:
            - Zone of the admin user
        required: true
        type: str

requirements:
    - python-irodsclient

author:
    - John Xu


"""

EXAMPLES = '''
# Create iRODS user of type rodsuser
- name: create user
  irods_user:
    name: test_user1
    state: present
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone

# Remove iRODS user
- name: remove user
  irods_user:
    name: test_user1
    state: absent
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone
'''

RETURN = '''
user:
    description: user that has been changed
    type: str
    returned: always
'''

try:
    USE_IRODS_CLIENT = True
    from irods.session import iRODSSession
    from irods.models import User
except ImportError:
    USE_IRODS_CLIENT = False


class IRODSUserModule:
    """
    Module class
    """

    def __init__(self):
        """
        Initialize the module
        """
        # define argument
        self.module_args = dict(
            name=dict(type="str", required=True),
            state=dict(type="str", required=True,
                       choices=["present", "absent"]),
            type=dict(type="str", default="rodsuser", required=False),
            password=dict(type="str", no_log=True, required=False),

            host=dict(type="str", required=True),
            port=dict(type="int", required=True),
            admin_user=dict(type="str", no_log=True, required=True),
            admin_password=dict(type="str", no_log=True, required=True),
            zone=dict(type="str", required=True),
        )
        # result
        self.result = dict(
            changed=False,
            user=""
        )

        # init module
        self.module = AnsibleModule(
            argument_spec=self.module_args,
            supports_check_mode=True
        )

        self.session = None

    def run(self):
        """
        Entry point for module class, method to be called to run the module
        """
        # check param and env
        self.sanity_check()

        # only-check mode
        if self.module.check_mode:
            self.module.exit_json(**self.result)

        self.init_session()

        action = self.select_action()
        action()

    def _fail(self, msg, err=None):
        """
        Failure routine, called when the operation failed
        """
        if self.session:
            self.session.cleanup()

        if err:
            self.module.fail_json(msg=msg + "\n" + str(err), **self.result)
        else:
            self.module.fail_json(msg=msg, **self.result)

    def _success(self, msg=""):
        """
        Success routine, called when the operation succeeds
        """
        if msg:
            self.result["message"] = msg
        self.module.exit_json(**self.result)

    def sanity_check(self):
        """
        Check if python-irodsclient is installed
        """
        # python-irodsclient is required at this point
        if not USE_IRODS_CLIENT:
            self._fail("python-irodsclient not installed")

    def init_session(self):
        """
        Initialize the iRODS session with iRODS server
        """
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None,
            cadata=None)
        ssl_settings = {"ssl_context": ssl_context}
        self.session = iRODSSession(
            host=self.module.params["host"],
            port=self.module.params["port"],
            user=self.module.params["admin_user"],
            password=self.module.params["admin_password"],
            zone=self.module.params["zone"],
            **ssl_settings)

    def select_action(self):
        """
        Dispatch action according to the argument passed to the module
        """
        if self.module.params["state"] == "present":
            return self.user_present
        return self.user_absent

    def user_present(self):
        """
        Ensure user specified in the parameter are present
        """
        # get username
        username = self.module.params["name"]
        if not username:
            self._success("empty username")
        user_type = self.module.params["type"]
        password = self.module.params["password"]

        # check if user exist
        if not self._user_exist(username):
            # create user
            self._create_user(username, user_type)
            if password:
                self._update_user_password(username, password)
            self.result["user"] = username
        elif self._user_type(username) != user_type:
            # update user_type
            self._update_user_type(username, user_type)
            self.result["user"] = username

        # check if user is present
        if not self._user_exist(username):
            self._fail("user disappear after creation, {}".format(username))
        self._success()

    def user_absent(self):
        """
        Ensure user specified in the parameter are absent
        """
        # get username
        username = self.module.params["name"]

        # check if user exist
        if not self._user_exist(username):
            self._success("user already absent")

        # remove user
        self._remove_user(username)
        self.result["user"] = username

        # check if user have been removed
        if self._user_exist(username):
            self._fail("user still exist after removal, {}".format(username))

    def _create_user(self, username, user_type):
        """
        Create an iRODS user with the given username
        """
        try:
            self.session.users.create(username, user_type)
            self.result["changed"] = True
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to create user {}".format(username), exc)

    def _update_user_type(self, username, user_type):
        """
        Update user's type
        """
        try:
            self.session.users.modify(username, "type", user_type)
            self.result["changed"] = True
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to update user type for {}".format(username), exc)

    def _update_user_password(self, username, password):
        """
        Update user's password
        """
        try:
            self.session.users.modify(username, "password", password)
            self.result["changed"] = True
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to update passowrd for user {}".format(username), exc)

    def _remove_user(self, username):
        """
        Remove the iRODS user with the given username
        """
        try:
            self.session.users.remove(username)
            self.result["changed"] = True
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to remove user {}".format(username), exc)

    def _user_type(self, username):
        """
        Get the type of the user, None if user not exists
        """
        try:
            user = self.session.users.get(username)
            if not user:
                return None
            return user.type
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to query user type for {}".format(username), exc)

    def _user_exist(self, username):
        """
        Check if there exist an iRODS user with the given username
        """
        try:
            query = self.session.query(User.name)

            for result in query:
                if username == result[User.name]:
                    return True
            return False
        except Exception as exc:
            # A broad catch on all exception type that could be raised by the
            # call to irods module, since the possible exception types are
            # not well documented.
            self._fail("Unable to query irods user {}".format(username), exc)


def main():
    """
    Entrypoint of the Ansible module
    """
    module = IRODSUserModule()
    module.run()


if __name__ == '__main__':
    main()
