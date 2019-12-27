Feature: Using completion.

    Scenario: Using library command completion.
        Given I open any directory
        When I run command
        Then the completion model should be command
        And the model mode should be library

    Scenario: Using image command completion.
        Given I open any image
        When I run command
        Then the completion model should be command
        And the model mode should be image

    Scenario: Using path completion.
        Given I open any directory
        When I run command --text="open "
        Then the completion model should be path

    Scenario: Using setting completion.
        Given I open any directory
        When I run command --text="set "
        Then the completion model should be settings

    Scenario: Using setting option completion.
        Given I open any directory
        When I run command --text="set shuffle"
        Then the completion model should be settings_option

    Scenario: Using trash completion.
        Given I open any directory
        When I run command --text="undelete "
        Then the completion model should be trash

    Scenario: Using tag completion with tag-delete.
        Given I open any directory
        When I run command --text="tag-delete "
        Then the completion model should be tag

    Scenario: Using tag completion with tag-load.
        Given I open any directory
        When I run command --text="tag-load "
        Then the completion model should be tag

    Scenario: Using tag completion with tag-write.
        Given I open any directory
        When I run command --text="tag-write "
        Then the completion model should be tag

    Scenario: Using help completion
        Given I open any directory
        When I run command --text="help "
        Then the completion model should be help
        And a possible completion should contain :open-selected
        And a possible completion should contain library.width
        And a possible completion should contain vimiv

    Scenario: Using external command completion
        Given I open any directory
        When I run command --text="!"
        Then the completion model should be external
        And a possible completion should contain !ls

    Scenario: Crash on path completion with non-existent directory
        Given I open any directory
        When I run command --text="open /not/a/valid/path"
        Then no crash should happen

    Scenario: Reset completions when leaving command mode
        Given I open any directory
        When I run command
        And I run complete
        And I run leave-commandline
        Then no completion should be selected

    Scenario: Crash when completing on entered number
        Given I open any directory
        When I run command --text="2"
        And I run complete
        Then no crash should happen

    Scenario: Do not use path completion on open-
        Given I open any directory
        When I run command --text="open-"
        Then the completion model should be command

    Scenario: Do not show hidden setting in completion.
        Given I open any directory
        When I run command --text="set history_li"
        And I run complete
        Then no completion should be selected

    Scenario: Escape path with spaces upon completion
        Given I open any directory
        When I run !mkdir 'path with spaces'
        And I wait for the command to complete
        And I run command --text="open pat"
        And I run complete
        And I activate the command line
        Then the working directory should be path with spaces

    Scenario: Update setting completion with newest value
        Given I open any directory
        When I run set slideshow.delay 42
        And I run command --text="set slideshow.delay"
        And I run complete
        Then a possible completion should contain 42

    Scenario: Using fuzzy completion filtering
        Given I open any directory
        When I run set completion.fuzzy true
        And I run command
        And I press flscrn
        Then a possible completion should contain fullscreen

    Scenario: Bug adding the current value multiple times to setting value suggestions
        Given I open any directory
        When I run set library.width +0.05
        And I run set library.width +0.05
        And I run command --text="set library.width"
        And I run complete
        Then there should be 6 completion options

    Scenario: Do not show trash completion in manipulate mode
        Given I open any image
        When I enter manipulate mode
        And I run command --text="undelete "
        Then the completion model should be command

    Scenario: Complete an existing tag
        Given I start vimiv
        When I run tag-write my_tag_name
        And I run command --text="tag-load "
        Then the completion model should be tag
        And there should be 1 completion options
        And a possible completion should contain my_tag_name

    Scenario: Show correct completion after changing mode
        Given I open any image
        When I run command
        And I activate the command line
        And I enter library mode
        And I run command
        Then the completion model should be command
        And a possible completion should contain open-selected

    Scenario: Relative path completion
        Given I open a directory with 5 paths
        When I run command --text="open ./"
        Then the completion model should be path
        And a possible completion should contain ./child_01

    Scenario: Relative path completion with fuzzy filtering
        Given I open a directory with 3 paths
        When I run set completion.fuzzy true
        And I run command --text="open ./cld"
        Then the completion model should be path
        And a possible completion should contain ./child_01

    Scenario: Show command completion after running invalid command
        Given I start vimiv
        When I run command
        And I press notacommand
        And I activate the command line
        And I run command
        Then the completion model should be command
        And a possible completion should contain open-selected

    Scenario: Command completion with count
        Given I start vimiv
        When I run command
        And I press 2got
        And I run complete
        Then the text in the command line should be :2goto
