Feature: Repeat the last command.

    Background:
        Given I start vimiv

    Scenario: Repeat command
        When I run count
        And I run repeat-command
        Then the count should be 2

    Scenario: Repeat command with given count.
        When I run count
        And I run 2repeat-command
        Then the count should be 3

    Scenario: Repeat command with stored count.
        When I run 2count
        And I run repeat-command
        Then the count should be 4

    Scenario: Display error message when running repeat-command before running anything.
        When I run repeat-command
        Then no crash should happen
        And the message
            'repeat-command: No command to repeat'
            should be displayed

    Scenario: Display error message when running repeat-command in other mode.
        When I run count
        And I enter image mode
        When I run repeat-command
        Then no crash should happen
        And the message
            'repeat-command: No command to repeat'
            should be displayed
