#!/bin/bash
# Run AAHB test suite

echo "Starting AAHB Test Suite"
echo "=============================="

# Set environment
export ENV=testing
export PYTHONPATH=$(pwd):$PYTHONPATH

# Run unit tests
echo "Running unit tests..."
pytest tests/unit -v --cov --cov-report=html:coverage/unit

# Run integration tests
echo "Running integration tests..."
pytest tests/integration -v --cov --cov-append --cov-report=html:coverage/integration

# Run performance tests (not included in coverage)
echo "Running performance tests..."
pytest tests/performance -v

echo "Test suite completed"
echo "Coverage report: file://$(pwd)/coverage/index.html"