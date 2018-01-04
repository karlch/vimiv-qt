Feature: Switching between different modes.

    Scenario: Enter command mode from library
        Given I open any directory
        When I enter command mode
        Then the mode should be command

    Scenario: Enter and leave command mode from library
        Given I open any directory
        When I enter command mode
        And I leave command mode
        Then the mode should be library

    Scenario: Enter image mode from library
        Given I open any directory
        When I enter image mode
        Then the mode should be image

    Scenario: Enter library from image
        Given I open any image
        When I enter library mode
        Then the mode should be library

    Scenario: Enter thumbnail from image
        Given I open any image
        When I enter thumbnail mode
        Then the mode should be thumbnail
