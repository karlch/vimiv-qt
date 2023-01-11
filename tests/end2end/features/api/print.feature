Feature: Print to STDOUT

    Scenario: Print trivial list
        Given I start vimiv
        And I capture output
        When I run print-stdout "test"
        Then stdout should contain 'test'

    Scenario: Print longer list
        Given I start vimiv
        And I capture output
        When I run print-stdout "test1" "test2"
        Then stdout should contain 'test1'
        And stdout should contain 'test2'

    Scenario: Print list using sep
        Given I start vimiv
        And I capture output
        When I run print-stdout "test1" "test2" --sep ','
        Then stdout should contain 'test1,test2'

    Scenario: Print list using end
        Given I start vimiv
        And I capture output
        When I run print-stdout "test1" "test2" --end 'xxx\n'
        Then stdout should contain 'test2xxx'

    Scenario: Print marked images
        Given I open 2 images
        And I capture output
        When I run mark image_01.jpg image_02.jpg
        And I run print-stdout %m
        Then stdout should contain 'image_01.jpg'
        And stdout should contain 'image_02.jpg'

    Scenario: Print marked images using alias
        Given I open 2 images
        And I capture output
        When I run mark image_01.jpg image_02.jpg
        And I run mark-print
        Then stdout should contain 'image_01.jpg'
        And stdout should contain 'image_02.jpg'
