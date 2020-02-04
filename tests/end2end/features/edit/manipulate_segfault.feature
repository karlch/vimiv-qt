Feature: Segfault when manipulating an image.

    Scenario: Segfault when applying manipulations to images larger than screen-size
        Given I open any image of size 1200x900
        When I enter manipulate mode
        And I apply any manipulation
        And I run accept
        Then no crash should happen
