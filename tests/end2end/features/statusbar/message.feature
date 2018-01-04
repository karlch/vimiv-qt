Feature: Push messages to the statusbar.

    Background:
        Given I open any directory

    Scenario: Display warning message.
        When I log the warning 'this is a warning'
        Then the message
            'this is a warning'
            should be displayed
