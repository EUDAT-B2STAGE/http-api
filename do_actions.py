# -*- coding: utf-8 -*-


class InvalidArgument(BaseException):
    pass


class NotImplementedAction(BaseException):
    pass


class ImplementedActions:

    def _exec(command):
        print ("\nCommand to be executed:\n\tdocker-compose %s\n\n" % command)

    def service_mandatory(service):
        if service is None:
            raise InvalidArgument(
                'Service parameters is mandatory for this action'
            )

    def service_incompatible(service):
        if service is not None:
            raise InvalidArgument(
                'Service parameter is incompatible with this action'
            )

    def do_check(project, action, service):
        ImplementedActions.service_incompatible(service)
        raise NotImplemented(
            'verify if the %s blueprint is well-configured' % project
        )

    def do_init(command, project, action, service):
        ImplementedActions.service_incompatible(service)
        raise NotImplemented(
            'init the %s blueprint (in old do command)' % project
        )

    def do_update(command, action, service):
        ImplementedActions.service_incompatible(service)

        ImplementedActions._exec("%s %s" % (command, action))

    def do_start(command, action, service):
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_stop(command, action, service):
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_restart(command, action, service,):
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_graceful(command, action, service):
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_scale(command, action, service, num):
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec(
            "%s %s %s=%s" % (command, action, service, num))

    def do_logs(command, action, service):
        if service is None:
            ImplementedActions._exec("%s %s" % (command, action))
        else:
            ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_remove(command, action, service):
        # service is required or not for this action?
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_clean(command, action, service):
        # service is required or not for this action?
        ImplementedActions.service_mandatory(service)
        ImplementedActions._exec("%s %s %s" % (command, action, service))

    def do_command(command, action, service, arguments):
        ImplementedActions.service_mandatory(service)
        if len(arguments) == 0:
            raise InvalidArgument('Missing arguments for command action')

        ImplementedActions._exec(
            "%s exec %s %s" % (command, service, arguments))

    def do_shell(command, action, service):
        ImplementedActions.service_mandatory(service)
        ImplementedActions.do_command(
            command, action, service, arguments='bash')

    def do_bower(command, action, service, arguments):
        ImplementedActions.service_incompatible(service)
        if len(arguments) == 0:
            raise InvalidArgument('Missing arguments for bower action')

        ImplementedActions.do_command(
            command, action, service='bower', arguments=arguments)
