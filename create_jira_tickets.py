#!/usr/bin/env python3
"""
Jira Ticket Creation Script for API Test Failures
Creates bug tickets in DEX project for critical API test failures
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from analyze_test_failures import TestFailureAnalyzer

class JiraTicketCreator:
    def __init__(self):
        self.cloud_id = "e9ed7bab-c21a-4b0c-b996-fa7146d8e58b"
        self.project_key = "DX"
        self.created_tickets = []
        
    def create_tickets_for_failures(self, failures: list, max_tickets: int = 15) -> list:
        """Create Jira tickets for failures"""
        
        analyzer = TestFailureAnalyzer()
        created_tickets = []
        
        print(f"Creating Jira tickets for {min(len(failures), max_tickets)} failures...")
        
        for i, failure in enumerate(failures[:max_tickets], 1):
            try:
                ticket_data = analyzer.generate_jira_ticket_data(failure)
                
                print(f"\n{i}. Creating ticket for: {failure['test_suite']} - {failure['test_name']}")
                print(f"   Severity: {failure['severity']} | Response Code: {failure.get('response_code', 'N/A')}")
                
                # Map severity to Jira priority
                jira_priority = {
                    "Critical": "Highest",
                    "High": "High", 
                    "Medium": "Medium",
                    "Low": "Low"
                }.get(failure["severity"], "Medium")
                
                # Create the Jira ticket (we'll add the actual API call here)
                ticket_info = {
                    "ticket_data": ticket_data,
                    "failure": failure,
                    "priority": jira_priority,
                    "created": False,
                    "ticket_key": None,
                    "error": None
                }
                
                created_tickets.append(ticket_info)
                
            except Exception as e:
                print(f"Error preparing ticket for {failure['test_name']}: {str(e)}")
                
        return created_tickets
    
    def print_ticket_summary(self, tickets: list):
        """Print summary of tickets to be created"""
        
        print(f"\n{'='*80}")
        print("JIRA TICKET CREATION SUMMARY")
        print(f"{'='*80}")
        
        for i, ticket in enumerate(tickets, 1):
            failure = ticket['failure']
            data = ticket['ticket_data']
            
            print(f"\n{i}. TICKET: {data['summary']}")
            print(f"   Priority: {ticket['priority']}")
            print(f"   Test Suite: {failure['test_suite']}")
            print(f"   Test Name: {failure['test_name']}")
            print(f"   Response Code: {failure.get('response_code', 'N/A')}")
            print(f"   Failure Reason: {failure['failure_reason'][:100]}...")
            
            if ticket.get('ticket_key'):
                print(f"   Ticket Key: {ticket['ticket_key']}")
            
            if ticket.get('error'):
                print(f"   Error: {ticket['error']}")

def main():
    """Main execution"""
    
    # Load the analysis results
    analysis_file = Path("/home/ali/dex_agent/test_failure_analysis.json")
    if not analysis_file.exists():
        print("Error: test_failure_analysis.json not found. Run analyze_test_failures.py first.")
        return
    
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)
    
    # Get failures to create tickets for
    critical_failures = analysis.get("critical_failures", [])
    high_failures = analysis.get("high_priority_failures", [])
    
    # Prioritize critical first, then high
    failures_to_process = critical_failures + high_failures
    
    print(f"Found {len(critical_failures)} critical and {len(high_failures)} high priority failures")
    
    # Create ticket creator
    creator = JiraTicketCreator()
    
    # Prepare tickets (but don't create yet - we'll do that step by step)
    tickets = creator.create_tickets_for_failures(failures_to_process, max_tickets=15)
    
    # Print summary
    creator.print_ticket_summary(tickets)
    
    # Save ticket data for manual creation or later processing
    ticket_file = Path("/home/ali/dex_agent/jira_tickets_to_create.json")
    with open(ticket_file, 'w') as f:
        json.dump({
            "analysis_timestamp": analysis.get("analysis_timestamp"),
            "total_tickets_prepared": len(tickets),
            "critical_count": len([t for t in tickets if t['failure']['severity'] == 'Critical']),
            "high_count": len([t for t in tickets if t['failure']['severity'] == 'High']),
            "tickets": tickets
        }, f, indent=2)
    
    print(f"\n\nTicket data saved to: {ticket_file}")
    print("Ready to create Jira tickets using MCP integration.")
    
    return tickets

if __name__ == "__main__":
    tickets = main()