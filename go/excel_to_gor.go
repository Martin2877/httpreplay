package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"
)

// generateRequestID generates a unique request ID similar to the ones in the GOR file.
func generateRequestID() string {
	// Create a UUID and use part of its hex representation
	return uuid.New().String()[:24]
}

// getTimestamp gets current timestamp in nanoseconds.
func getTimestamp() int64 {
	return time.Now().UnixNano()
}

// extractRequestsFromExcel extracts HTTP requests from the Excel file and writes them to a GOR file.
func extractRequestsFromExcel(excelPath, outputPath, httpReqColumn string) (int, error) {
	// Open the Excel file
	f, err := excelize.OpenFile(excelPath)
	if err != nil {
		return 0, fmt.Errorf("failed to open Excel file: %v", err)
	}
	defer f.Close()

	// Get all the rows from the first sheet
	rows, err := f.GetRows(f.GetSheetList()[0])
	if err != nil {
		return 0, fmt.Errorf("failed to get rows from sheet: %v", err)
	}

	// Find the column index for the specified HTTP request column
	headers := rows[0]
	var httpReqCol int = -1
	for i, header := range headers {
		if header == httpReqColumn {
			httpReqCol = i
			break
		}
	}

	if httpReqCol == -1 {
		return 0, fmt.Errorf("column '%s' not found in the Excel file", httpReqColumn)
	}

	// Open output file
	outputFile, err := os.Create(outputPath)
	if err != nil {
		return 0, fmt.Errorf("failed to create output file: %v", err)
	}
	defer outputFile.Close()

	// Process each row (skip header)
	count := 0
	for i, row := range rows[1:] {
		if len(row) <= httpReqCol || strings.TrimSpace(row[httpReqCol]) == "" {
			continue
		}

		httpRequest := strings.TrimSpace(row[httpReqCol])
		requestID := generateRequestID()
		timestamp := getTimestamp()

		// Write the metadata line
		_, err = fmt.Fprintf(outputFile, "1 %s %d 0\n", requestID, timestamp)
		if err != nil {
			return count, fmt.Errorf("failed to write to output file: %v", err)
		}

		// Write the HTTP request
		_, err = fmt.Fprintf(outputFile, "%s\n", httpRequest)
		if err != nil {
			return count, fmt.Errorf("failed to write to output file: %v", err)
		}

		// Add separator if not the last request
		if i < len(rows)-2 { // -2 because we skipped the header
			_, err = fmt.Fprint(outputFile, "\n\n🐵🙈🙉\n")
			if err != nil {
				return count, fmt.Errorf("failed to write separator: %v", err)
			}
		}

		count++
	}

	// Add final separator
	_, err = fmt.Fprint(outputFile, "\n\n🐵🙈🙉\n")
	if err != nil {
		return count, fmt.Errorf("failed to write final separator: %v", err)
	}

	return count, nil
}

func main() {
	// Parse command line arguments
	inputFile := flag.String("input", "", "Path to the input Excel file")
	outputFile := flag.String("output", "", "Path to the output GOR file")
	httpReqColumn := flag.String("column", "http请求", "Name of the column containing HTTP requests")
	flag.Parse()

	// Validate input
	if *inputFile == "" || *outputFile == "" {
		log.Fatal("Both --input and --output parameters are required")
	}

	// Check if input file exists
	if _, err := os.Stat(*inputFile); os.IsNotExist(err) {
		log.Fatalf("Input file %s does not exist", *inputFile)
	}

	// Process the Excel file
	count, err := extractRequestsFromExcel(*inputFile, *outputFile, *httpReqColumn)
	if err != nil {
		log.Fatalf("Error processing file: %v", err)
	}

	log.Printf("Successfully wrote %d requests to %s\n", count, *outputFile)
}
