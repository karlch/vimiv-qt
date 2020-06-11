Feature: Using completion.

    Scenario: Using library command completion.
        Given I open any directory
        When I run command
        Then a possible completion should contain open-selected

    Scenario: Using image command completion.
        Given I open any image
        When I run command
        Then a possible completion should contain center

    Scenario: Command completion with count
        Given I start vimiv
        When I run command
        And I press '2got'
        And I run complete
        Then the text in the command line should be :2goto

    Scenario: Crash when completing on entered number
        Given I open any directory
        When I run command --text="2"
        And I run complete
        Then no crash should happen

    Scenario: Show correct completion after changing mode
        Given I open any image
        When I run command
        And I press '<return>'
        And I enter library mode
        And I run command
        Then a possible completion should contain open-selected

    Scenario: Show command completion after running invalid command
        Given I start vimiv
        When I run command
        And I press 'notacommand'
        And I press '<return>'
        And I run command
        Then a possible completion should contain open-selected

    Scenario: Using path completion.
        Given I open a directory with 2 paths
        When I run command --text="open "
        Then a possible completion should contain open ./child_01
        And a possible completion should contain open ./child_02

    Scenario: Relative path completion with fuzzy filtering
        Given I open a directory with 3 paths
        When I run set completion.fuzzy true
        And I run command --text="open ./cld1"
        Then there should be 1 completion option
        And a possible completion should contain ./child_01

    Scenario: Crash on path completion with non-existent directory
        Given I open any directory
        When I run command --text="open /not/a/valid/path"
        Then no crash should happen

    Scenario: Do not use path completion on open-
        Given I open any directory
        When I run command --text="open-"
        Then a possible completion should contain open-selected

    Scenario: Escape path with spaces upon completion
        Given I open any directory
        When I create the directory 'path with spaces'
        And I run command --text="open pat"
        And I run complete
        And I press '<return>'
        Then the working directory should be path with spaces

    Scenario: Escape path with backslashes upon completion
        Given I open any directory
        When I create the directory 'path\with\backslashes'
        And I run command --text="open pat"
        And I run complete
        And I press '<return>'
        Then the working directory should be path\with\backslashes

    Scenario: Escape path with percent upon completion
        Given I open any directory
        When I create the directory 'directory%'
        And I run command --text="open dir"
        And I run complete
        And I press '<return>'
        Then the working directory should be directory%

    Scenario: Escape path with backslash and subsequent percent upon completion
        Given I open any directory
        When I create the directory 'directory\%'
        And I run command --text="open dir"
        And I run complete
        And I press '<return>'
        Then the working directory should be directory\%

    Scenario: Complete from directory with escaped characters
        Given I open any directory
        When I create the directory 'path\with\backslashes/child'
        And I run command --text="open pat"
        And I run complete
        And I press '/'
        Then a possible completion should contain open ./path\\with\\backslashes/child

    Scenario: Using setting completion.
        Given I open any directory
        When I run command --text="set "
        Then a possible completion should contain set shuffle
        And a possible completion should contain set library.width

    Scenario: Do not show hidden setting in completion.
        Given I open any directory
        When I run command --text="set history_li"
        And I run complete
        Then no completion should be selected

    Scenario: Using setting option completion.
        Given I open any directory
        When I run command --text="set shuffle"
        Then a possible completion should contain set shuffle True
        And a possible completion should contain set shuffle False

    Scenario: Update setting completion with newest value
        Given I open any directory
        When I run set slideshow.delay 42
        And I run command --text="set slideshow.delay"
        And I run complete
        Then a possible completion should contain 42

    Scenario: Bug adding the current value multiple times to setting value suggestions
        Given I open any directory
        When I run set library.width +0.05
        And I run set library.width +0.05
        And I run command --text="set library.width"
        And I run complete
        Then there should be 6 completion options

    Scenario: Using trash completion.
        Given I open a directory with 2 images
        When I run delete %
        When I run command --text="undelete "
        Then a possible completion should contain undelete image_01.jpg
        And the trash completion for 'image_01.jpg' should show the trashinfo

    Scenario: Do not show trash completion in manipulate mode
        Given I open 2 images
        When I run delete %
        And I enter manipulate mode
        And I run command --text="undelete "
        Then there should be 0 completion options

    Scenario: Using tag completion with tag-load.
        Given I open any directory
        When I create the tag file 'test-tag'
        And I run command --text="tag-load "
        Then there should be 1 completion option
        And a possible completion should contain tag-load test-tag

    Scenario: Using tag completion with tag-delete.
        Given I open any directory
        When I create the tag file 'test-tag'
        And I run command --text="tag-delete "
        Then there should be 1 completion option
        And a possible completion should contain tag-delete test-tag

    Scenario: Using tag completion with tag-write.
        Given I open any directory
        When I create the tag file 'test-tag'
        And I run command --text="tag-write "
        Then there should be 1 completion option
        And a possible completion should contain tag-write test-tag

    Scenario: Using help completion
        Given I open any directory
        When I run command --text="help "
        Then a possible completion should contain help :open-selected
        And a possible completion should contain help library.width
        And a possible completion should contain help  vimiv

    Scenario: Using external command completion
        Given I open any directory
        When I run command --text="!"
        Then a possible completion should contain !ls

    Scenario: Reset completions when leaving command mode
        Given I open any directory
        When I run command
        And I run complete
        And I run leave-commandline
        Then no completion should be selected

    Scenario: Using fuzzy completion filtering
        Given I open any directory
        When I run set completion.fuzzy true
        And I run command
        And I press 'flscrn'
        Then a possible completion should contain fullscreen

    Scenario: Ensure completion is case insensitive
        Given I start vimiv
        When I run command --text="Fulls"
        Then a possible completion should contain fullscreen

    Scenario: Ensure fuzzy completion is case insensitive
        Given I start vimiv
        When I run set completion.fuzzy true
        And I run command --text="FLS"
        Then a possible completion should contain fullscreen

    Scenario: Select first row upon complete
        Given I start vimiv
        When I run command
        And I run complete
        Then the completion row number 0 should be selected

    Scenario: Select second row upon two completions
        Given I start vimiv
        When I run command
        And I run complete
        And I run complete
        Then the completion row number 1 should be selected

    Scenario: Select last row upon complete --inverse
        Given I start vimiv
        When I run command
        And I run complete --inverse
        Then the completion row number -1 should be selected
