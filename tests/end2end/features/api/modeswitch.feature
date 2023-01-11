Feature: Switching between different modes.

    Scenario: Enter command mode from library
        Given I open any directory
        When I enter command mode
        Then the mode should be command

    Scenario: Enter and close command mode from library
        Given I open any directory
        When I enter command mode
        And I close command mode
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

    Scenario: Do not re-open a closed mode implicitly
        Given I open any image
        When I enter thumbnail mode
        And I enter library mode
        And I enter thumbnail mode
        And I toggle thumbnail mode
        And I toggle library mode
        Then the mode should be image

    Scenario: Do not crash on invalid mode name
        Given I start vimiv
        When I run enter invalid
        Then no crash should happen

    # This is ambiguous as we do not know if the user wishes to search or to enter a
    # command
    Scenario: Do not allow entering command mode using enter
        Given I start vimiv
        When I run enter command
        Then the mode should be library
        And the message
            'enter: Entering command mode is ambiguous, please use :command or :search'
            should be displayed

    Scenario: Do not switch mode when toggling inactive library mode
        Given I start vimiv
        When I toggle thumbnail mode
        # This used to enter image as image was the mode "before" library
        And I toggle library mode
        Then the mode should be thumbnail

    Scenario: Do not switch mode when toggling inactive thumbnail mode
        Given I open 2 images
        When I toggle thumbnail mode
        When I toggle library mode
        # This used to enter image as image was the mode "before" thumbnail
        And I toggle thumbnail mode
        Then the mode should be library

    Scenario: Crash when toggling manipulate mode
        Given I open 2 images
        When I toggle manipulate mode
        Then no crash should happen
        And the mode should be manipulate
