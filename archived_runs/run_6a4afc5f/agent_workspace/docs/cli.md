# CEOBench CLI Reference

## novamind-operation

Entry point for novamind-operation CLI.

Commands:
    next-week   Advance the simulator by one week (7 days)
    next-day    Alias for next-week (backward compat)

Examples:
    ./novamind-operation next-week


### Commands

#### `./novamind-operation next-day`

Advance the simulator to the next day.

Calls the API server to step the simulation forward by one day.
Prints the dashboard to stdout, which includes key metrics,
yesterday's results, and inbox notifications.

**What happens each day (in order):**
1. Daily calculations run (if registered)
2. New customers spawned based on marketing + reputation
3. Customers at billing day re-evaluate plans (may switch/cancel)
4. Usage simulated, compute costs incurred
5. Service metrics calculated (latency, errors, outages)
6. Revenue collected from billing customers
7. Fixed costs deducted (capacity, operations, development, advertising)
8. Social posts generated based on satisfaction
9. Enterprise negotiations processed (customer replies, timeouts)
10. VC negotiations processed (counter-offers delivered)
11. Each predefined VC independently rolls for daily approach
12. Deal expiry processed (accepted-but-unsettled deals + stale threads)
13. Reputation updated
14. Dashboard built and returned

**Dashboard includes:** CASH, MRR, SUBSCRIBERS, yesterday's metrics
(revenue, costs, new/cancelled subs, usage, overload, outages), INBOX
(new notifications), and current config summary.

**NOTE:** The next_week call may take several minutes at large subscriber
counts. This is normal — just wait for the response.

Exit code 0 on success, 1 on failure.

## novamind

Entry point for novamind CLI.

Commands:
    register-daily-script   Register a script to run daily
    list-daily-scripts      List all registered daily scripts
    remove-daily-script     Remove a registered daily script

Examples:
    novamind register-daily-script strategy.py
    novamind list-daily-scripts
    novamind remove-daily-script strategy.py


### Commands

#### `novamind register-daily-script`

Register a Python script to run automatically at the start of each day.

The script content is snapshotted at registration time. Subsequent edits
to the source file will NOT affect the registered version. To update,
re-register the script.

If a script with the same filename already exists, it is overwritten.
Scripts are executed in alphabetical order at the start of each day,
with novamind_api pre-imported.

Args:
    script_path: Path to the Python script to register.

Example:
    novamind register-daily-script my_strategy.py

#### `novamind list-daily-scripts`

List all registered daily scripts.

Shows script names and sizes. Scripts run at the start of each day
in alphabetical order.

Example:
    novamind list-daily-scripts

#### `novamind remove-daily-script`

Remove a registered daily script.

Args:
    script_name: Filename of the script to remove.

Example:
    novamind remove-daily-script my_strategy.py
