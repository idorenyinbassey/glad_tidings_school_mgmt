#!/bin/bash

# Glad Tidings School Management Portal Test Runner
# Now supports both Django test runner and pytest

# Function to run tests with error handling
run_test_suite() {
    local test_name=$1
    local test_path=$2
    local verbosity=${3:-1}
    
    echo "Running $test_name for Glad Tidings School Management Portal"
    echo "=============================================================="
    
    # Use pytest if available, otherwise fall back to Django's test runner
    if command -v pytest >/dev/null 2>&1; then
        python -m pytest $test_path -v
    else
        python manage.py test $test_path --verbosity=$verbosity
    fi
    
    # Check if the tests passed
    if [ $? -eq 0 ]; then
        echo "✅ $test_name completed successfully!"
    else
        echo "❌ $test_name had failures!"
    fi
    echo ""
}

# Default behavior - run all test suites
if [ "$1" != "fixed-core-only" ]; then
    run_test_suite "Core Django Tests" "core" 2
    run_test_suite "Enhanced Tests" "core.tests_enhanced"
    run_test_suite "API Tests" "core.tests_api"
    run_test_suite "Mobile Responsiveness Tests" "core.tests_mobile"
else
    # Run only the fixed core tests
    run_test_suite "Fixed Core Django Tests" "core" 2
fi

# Check for command-line arguments to run specific test cases
if [ $# -gt 0 ]; then
    case $1 in
        "url")
            run_test_suite "URL Access Tests" "core.tests_enhanced.UrlAccessTestCase"
            ;;
        "security")
            run_test_suite "Security Tests" "core.tests_enhanced.SecurityTestCase"
            ;;
        "responsive")
            run_test_suite "Responsive Design Tests" "core.tests_enhanced.ResponsiveDesignTestCase"
            ;;
        "features")
            run_test_suite "Feature Module Tests" "core.tests_enhanced.FeatureModuleTestCase"
            ;;
        "performance")
            run_test_suite "Performance Tests" "core.tests_enhanced.PerformanceTestCase"
            ;;
        "forms")
            run_test_suite "Form Validation Tests" "core.tests_enhanced.FormValidationTestCase"
            ;;
        "mobile")
            run_test_suite "Mobile Specific Tests" "core.tests_mobile"
            ;;
        "api")
            run_test_suite "API Tests" "core.tests_api"
            ;;
        "fixed-core-only")
            run_test_suite "Fixed Core Tests" "core" 2
            ;;
        "all-fixed")
            run_test_suite "Fixed Core Tests" "core" 2
            run_test_suite "Enhanced Tests" "core.tests_enhanced"
            run_test_suite "API Tests" "core.tests_api"
            run_test_suite "Mobile Tests" "core.tests_mobile"
            ;;
        *)
            echo "Unknown test category: $1"
            echo "Available categories: url, security, responsive, features, performance, forms, mobile, api, fixed-core-only, all-fixed"
            exit 1
            ;;
    esac
fi

echo "=============================================================="
echo "Tests completed!"
echo "To run specific test categories, use: ./run_tests.sh [category]"
echo "Available categories:"
echo "  url          - Test URL access with proper permissions"
echo "  security     - Test security features"
echo "  responsive   - Test responsive design"
echo "  features     - Test specific features/modules"
echo "  performance  - Test performance metrics"
echo "  forms        - Test form validations"
echo "  mobile       - Test mobile-specific functionality"
echo "  api          - Test API endpoints"
echo "  fixed-core-only - Run only core tests"
echo "  all-fixed    - Run all tests with fixes applied"
