Feature: The keyhint overlay widget

    Background:
        Given I start vimiv

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

    Scenario: Keyhint should be above statusbar
        When I press g
        And I wait for the keyhint widget
        Then the keyhint widget should be above the statusbar

    Scenario: Keyhint at bottom with statusbar hidden
        When I run set statusbar.show false
        And I press g
        And I wait for the keyhint widget
        Then the keyhint widget should be at the bottom

    Scenario: Do not show widget in command mode
        When I run command
        And I press <
        Then the keyhint widget should not appear

    Scenario: Keyhint widget cleared and hidden after escape
        When I press g
        And I wait for the keyhint widget
        And I press <escape>
        Then the keyhint widget should not be visible
