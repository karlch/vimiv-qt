Feature: Repeat the last command.

    Scenario: Repeat command in library mode.
        Given I open a directory with 5 paths
        When I run scroll down
        And I run repeat-command
        Then the library row should be 3

    Scenario: Repeat command with given count.
        Given I open a directory with 5 paths
        When I run scroll down
        And I run 2repeat-command
        Then the library row should be 4

    Scenario: Repeat command with stored count.
        Given I open a directory with 5 paths
        When I run 2scroll down
        And I run repeat-command
        Then the library row should be 5

    Scenario: Repeat command in image mode.
        Given I open 5 images
        When I run next
        And I run repeat-command
        Then the image should have the index 3

    Scenario: Display error message when running repeat-command before running anything.
        Given I start vimiv
        When I run repeat-command
        Then no crash should happen
        And the message
            'repeat-command: No command to repeat'
            should be displayed

    Scenario: Display error message when running repeat-command in other mode.
        Given I open a directory with 5 paths
        When I run scroll down
        And I enter image mode
        When I run repeat-command
        Then no crash should happen
        And the message
            'repeat-command: No command to repeat'
            should be displayed
