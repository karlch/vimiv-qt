Feature: Run miscellaneous commands.

    Background:
        Given I start vimiv

    Scenario: Log an info message
        When I run log info my message
        Then the message
            'my message'
            should be displayed

    Scenario: Log a warning message
        When I run log warning oh oh
        Then the message
            'oh oh'
            should be displayed

    Scenario: Log an error message
        When I run log error this is bad
        Then the message
            'this is bad'
            should be displayed

    Scenario: Fail logging a message
        When I run log basement spiders
        Then the message
            'log: Unknown log level 'basement''
            should be displayed

    Scenario: Sleep for some time
        Given I start a timer
        When I run sleep 0.01
        Then at least 0.01 seconds should have elapsed
