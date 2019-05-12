Feature: Open different image formats

    Background:
        Given I start vimiv

    Scenario: Error on invalid image formats
        When I open broken images
        Then no crash should happen
