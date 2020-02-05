Feature: Keybindings command with pop up window with the keybindings for current mode

    Scenario: Display the keybindings pop up for library mode.
        Given I start vimiv
        When I run keybindings
        Then the keybindings pop up should contain 'set library.width'
        And the pop up 'vimiv - keybindings' should be displayed

    Scenario: Display the keybindings pop up for image mode.
        Given I open 2 images
        When I run keybindings
        Then the keybindings pop up should contain 'flip'
        And the pop up 'vimiv - keybindings' should be displayed

    Scenario: Display the keybindings pop up for thumbnail mode.
        Given I open 2 images
        When I enter thumbnail mode
        And I run keybindings
        Then the keybindings pop up should contain 'zoom in'
        And the pop up 'vimiv - keybindings' should be displayed

    Scenario: Display the keybindings pop up for manipulate mode.
        Given I open 2 images
        When I enter manipulate mode
        And I run keybindings
        Then the keybindings pop up should contain 'accept'
        And the pop up 'vimiv - keybindings' should be displayed

    Scenario: Search the keybindins pop up
        Given I start vimiv
        When I run keybindings
        And I press 'comm' in the pop up
        Then 'comm' should be highlighted in 'command'
        Then the keybindings pop up should describe 'command'

    Scenario: Do not describe single command matches
        Given I start vimiv
        When I run keybindings
        And I press 'a' in the pop up
        Then the keybindings pop up description should be empty
