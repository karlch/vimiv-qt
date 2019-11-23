Feature: Transform an image.

    Scenario: Crash when running transform without image
        Given I start vimiv
        When I enter image mode
        And I run rotate
        Then no crash should happen
