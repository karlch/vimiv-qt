Feature: Display status information in the statusbar

    Scenario: Display image information
        Given I open 3 images
        Then the left status should include 1/3
        And the left status should include image_01.jpg
        And the right status should include IMAGE

    Scenario: Display library information
        Given I open any directory
        Then the left status should include directory
        And the right status should include LIBRARY

    Scenario: Display correct mode after switch
        Given I open any directory
        When I run enter image
        Then the right status should include IMAGE

    Scenario: Show filesize in statusbar
        Given I start vimiv
        When I run set statusbar.left {filesize}
        # No current path selected
        Then the left status should include N/A

    Scenario: Do not crash when showing filesize in command moe
        Given I start vimiv
        When I run set statusbar.left {filesize}
        And I run command
        Then no crash should happen

    Scenario: Correctly escape html for keybindings
        Given I start vimiv
        When I run bind << scroll down
        And I press '<'
        Then the right status should include &lt;

    Scenario: Show read-only mode in statusbar
        Given I start vimiv
        When I run set read_only true
        Then the left status should include [RO]
