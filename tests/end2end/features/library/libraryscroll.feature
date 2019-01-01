Feature: Scrolling the library.

    Scenario: Scroll up and down.
        Given I open a directory with 5 paths
        When I run scroll down
        And I run scroll down
        And I run scroll up
        Then the library row should be 2

    Scenario: Crash when scrolling empty directory.
        Given I open any directory
        When I run scroll down
        And I run scroll up
        Then no crash should happen
        And the message
            'scroll: Directory is empty'
            should be displayed

    Scenario: Crash when selecting file in empty directory.
        Given I open any directory
        When I run scroll right
        Then no crash should happen

    Scenario: Enter directory
        Given I open a directory with 1 paths
        When I run scroll right
        Then the working directory should be child_01

    Scenario: Enter and leave directory remembering position
        Given I open a directory with 2 paths
        When I run scroll down
        And I run scroll right
        And I run scroll left
        Then the library row should be 2
