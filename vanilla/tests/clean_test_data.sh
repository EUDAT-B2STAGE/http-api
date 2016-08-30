#!/bin/bash

echo "Cleaning"
sleep 1

# Coverage + stop on first failure
com="nose2 -F"
option="-s test"
cov_reports=" --coverage-report term --coverage-report html"
cov_options="-C --coverage restapi $cov_reports"

custom_test_file="test.custom.test_dataobjects"
clean_method="TestDataObjects.test_08_delete_dataobjects"
$com $custom_test_file.$clean_method
echo ""
echo "Cleaned"
