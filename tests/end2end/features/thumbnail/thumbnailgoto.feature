Feature: Select a specific thumbnail using the :goto command.

    Scenario: Select last thumbnail
        Given I open 10 images
        And I enter thumbnail mode
        When I run goto -1
        Then the thumbnail number 10 should be selected

    Scenario: Select last and then first thumbnail
        Given I open 10 images
        And I enter thumbnail mode
        When I run goto -1
        And I run goto 1
        Then the thumbnail number 1 should be selected

    Scenario: Select specific thumbnail using count
        Given I open 10 images
        And I enter thumbnail mode
        When I run 3goto
        Then the thumbnail number 3 should be selected

    Scenario: Crash on goto with empty thumbnail list
        Given I start vimiv
        When I enter thumbnail mode
        And I run goto 4
        Then no crash should happen
        And the message
            'goto: No thumbnail in list'
            should be displayed
