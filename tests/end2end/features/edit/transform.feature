Feature: Transform an image.

    Scenario: Crash when running transform without image
        Given I start vimiv
        When I enter image mode
        And I run rotate
        Then no crash should happen

    Scenario: Rotate landscape image
        Given I open any image of size 300x200
        When I run rotate
        Then the orientation should be portrait

    Scenario: Rotate landscape image twice
        Given I open any image of size 300x200
        When I run 2rotate
        Then the orientation should be landscape

    Scenario: Rotate portrait image three times counter-clockwise
        Given I open any image of size 200x300
        When I run 3rotate --counter-clockwise
        Then the orientation should be landscape
