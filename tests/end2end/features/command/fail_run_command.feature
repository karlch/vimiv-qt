Feature: Do not crash and display error message on failed commands.

    Background:
        Given I start vimiv

    Scenario: Crash when running unknown command.
        When I run foo
        Then no crash should happen
        And the message
            'foo: unknown command for mode library'
            should be displayed

    Scenario: Crash when running command with unknown arguments.
        When I run quit --now
        Then no crash should happen
        And the message
            'quit: Unrecognized arguments: --now'
            should be displayed

    Scenario: Crash when running command with missing positional argument.
        When I run scroll
        Then no crash should happen
        And the message
            'scroll: The following arguments are required: direction'
            should be displayed

    Scenario: Crash on plain number command
        When I run 3
        Then no crash should happen

    Scenario: Crash on unclosed quote
        When I run '
        Then no crash should happen

    Scenario: Crash on empty command
        When I run
        Then no crash should happen
