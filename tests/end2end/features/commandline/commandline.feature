Feature: Use the command line.

    Background:
        Given I start vimiv

    Scenario: Run a command from the command line.
        When I run command
        And I press fullscreen
        And I activate the command line
        Then the window should be fullscreen

    Scenario: Crash on empty command.
        When I run command
        And I activate the command line
        Then no crash should happen
        And the mode should not be command

    Scenario: Enter command line with text to set
        When I run command --text=next
        Then the text in the command line should be :next

    Scenario: Run through history completion
        When I run command --text=next
        And I activate the command line
        And I run command
        And I run history next
        Then the text in the command line should be :next

    Scenario: Use history substring search
        When I run command --text=next
        And I activate the command line
        And I run command --text=prev
        And I activate the command line
        And I run command --text=n
        And I run history-substr-search next
        Then the text in the command line should be :next

    Scenario: Close command line when prefix is deleted
        When I run command
        And I hit backspace
        Then the mode should not be command
