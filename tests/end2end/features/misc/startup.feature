Feature: Startup vimiv with various flags

    Scenario: Set an option using the commandline
        Given I start vimiv with -s completion.fuzzy true
        Then the boolean setting 'completion.fuzzy' should be 'true'

    Scenario: Set multiple options using the commandline
        Given I start vimiv with -s completion.fuzzy true -s sort.shuffle true
        Then the boolean setting 'completion.fuzzy' should be 'true'
        And the boolean setting 'sort.shuffle' should be 'true'

    Scenario: Set an unknown option using the commandline
        Given I start vimiv with -s not.a.setting true
        Then no crash should happen

    Scenario: Set a wrong option value using the commandline
        Given I start vimiv with -s completion.fuzzy 42
        Then no crash should happen

    Scenario: Print version information
        Given I capture output
        And I run vimiv --version
        Then the version information should be displayed

    Scenario Outline: Set log level
        Given I start vimiv with --log-level <level>
        Then the log level should be <level>

        Examples:
            | level    |
            | debug    |
            | info     |
            | warning  |
            | error    |
            | critical |

    Scenario: Open hidden image upon startup
        Given I open the image '.hidden.jpg'
        Then the filelist should contain 1 images

    Scenario: Pipe paths to vimiv
        Given I start vimiv passing 3 images via stdin
        Then the filelist should contain 3 images

    Scenario: Start with an invalid file
        Given I open a text file
        Then no crash should happen
        And the mode should be library
        And the filelist should contain 0 images

    Scenario: Read binary image from stdin
        Given I start vimiv passing a binary image via stdin
        Then the mode should be image
        And the filelist should contain 1 images
