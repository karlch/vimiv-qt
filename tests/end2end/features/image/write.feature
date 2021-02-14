Feature: Write an image to disk

    Scenario Outline: Write image to new path
        Given I open any image
        When I write the image to <name>
        Then the file <name> should exist

        Examples:
            | name          |
            | new_path.jpg  |
            | new_path.png  |
            | new_path.tiff |

    @exif
    Scenario: Write image preserving exif information
        Given I open any image
        When I add exif information
        And I write the image to new_path.jpg
        Then the image new_path.jpg should contain exif information

    Scenario: Prompt for writing edited image
        Given I open any image
        When I run rotate
        And I plan to answer the prompt with n
        And I run next
        Then no crash should happen

    Scenario: Crash when writing image with tilde in path
        Given I open any image
        When I write the image to ~/test.jpg
        Then no crash should happen
        And the home directory should contain test.jpg
