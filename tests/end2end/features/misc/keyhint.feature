Feature: The keyhint overlay widget

    Background:
        Given I start vimiv
        And I re-initialize the keyhint widget

    Scenario: Display widget on partial keybindings
        When I press g
        And I wait for the keyhint widget
        Then the keyhint widget should be visible

    Scenario: Keyhint widget contains partial matches
        When I press g
        Then the keyhint widget should contain goto 1
        And the keyhint widget should contain enter image

    Scenario: Keyhint widget cleared and hidden after timeout
        When I press g
        And I wait for the keyhint widget
        And I wait for the keyhint widget timeout
        Then the keyhint widget should not be visible
