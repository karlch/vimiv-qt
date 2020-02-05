Feature: Use the command line.

    Background:
        Given I start vimiv

    Scenario: Set prefix correctly when entering command mode
        When I run command
        Then the text in the command line should be :

    Scenario: Run a command from the command line.
        When I run command
        And I press 'fullscreen'
        And I press '<return>'
        Then the window should be fullscreen

    Scenario: Crash on empty command.
        When I run command
        And I press '<return>'
        Then no crash should happen
        And the mode should not be command

    Scenario: Enter command line with text to set
        When I run command --text=next
        Then the text in the command line should be :next

    Scenario: Run through history completion
        When I run command --text=next
        And I press '<return>'
        And I run command
        And I run history next
        Then the text in the command line should be :next

    Scenario: Press through history completion
        When I run command --text=next
        And I press '<return>'
        And I run command
        And I press '<ctrl>p'
        Then the text in the command line should be :next

    Scenario: Use history substring search
        When I run command --text=next
        And I press '<return>'
        And I run command --text=prev
        And I press '<return>'
        And I run command --text=n
        And I run history-substr-search next
        Then the text in the command line should be :next

    Scenario: Do not remove prefix on empty history
        When I run command
        And I run history next
        Then the text in the command line should be :

    Scenario: Do not mix search and command history
        When I run command --text next
        And I press '<return>'
        And I run search
        And I run history next
        Then the text in the command line should be /

    Scenario: Close command line when prefix is deleted
        When I run command
        And I press '<backspace>'
        Then the mode should not be command

    Scenario: Show command help on -h
        When I run command --text='open-selected -h'
        And I press '<return>'
        Then the help for 'open-selected' should be displayed

    Scenario Outline: Show help using help command
        When I run help <topic>
        Then the help for '<topic>' should be displayed

        Examples:
            | topic          |
            | :open-selected |
            | vimiv          |
            | library.width  |

    Scenario: Fail help command with unknown topic
        When I run help invalid_topic
        Then the message
            'help: Unknown topic 'invalid_topic''
            should be displayed
