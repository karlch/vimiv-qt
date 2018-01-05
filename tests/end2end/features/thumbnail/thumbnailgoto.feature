Feature: Select a specific thumbnail using the :goto command.

    Background:
        Given I open 10 images
        And I enter thumbnail mode

    Scenario: Select last thumbnail
        When I run goto -1
        Then the thumbnail number 10 should be selected

    Scenario: Select last and then first thumbnail
        When I run goto -1
        And I run goto 1
        Then the thumbnail number 1 should be selected

    Scenario: Select specific thumbnail using count
        When I run 3goto 1
        Then the thumbnail number 3 should be selected
