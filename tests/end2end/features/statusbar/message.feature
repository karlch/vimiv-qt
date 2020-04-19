Feature: Push messages to the statusbar.

    Background:
        Given I open any directory

    Scenario: Display warning message.
        When I log the warning 'this is a warning'
        Then the message
            'this is a warning'
            should be displayed

    Scenario: Hide message widget when clearing status
        When I log the warning 'this is a warning'
        And I clear the status
        Then no message should be displayed

    Scenario: Clear message after key press
        When I log the warning 'this is a warning'
        And I press '0'
        Then no message should be displayed
