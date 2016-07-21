import unittest
from CookedZip.Spoon import Spoon


class SpoonTests(unittest.TestCase):

    def test_fix_inner_link(self):
        #with open('mock/Frequency,_Frequency_Tables,_and_Levels_of_Measurement.html', 'r') as content_file:
        with open('mock/3fb20c92-9515-420b-ab5e-6de221b89e99.html', 'r') as content_file:
            content = content_file.read()
            spoon = Spoon()
            html = spoon.fix_inner_link(content)
            print html

    def test_save_resource(self):
        spoon = Spoon()
        spoon.save_resource('http://archive-cte-cnx-dev.cnx.org/resources/77d8dd2e091a01c712087290565762f9b4c3f05a','')

    def test_local_url_format(self):
        spoon = Spoon()
        print spoon.local_url_format('12.3 | Testing the Significance of the Correlation Coefficient')
        print spoon.local_url_format('1.1 | Definitions of Statistics, Probability, and Key Terms')


def main():
    unittest.main()

if __name__ == '__main__':
    main()



