/
 * BrewNest Coffee Chain - SAS Analysis
 * Activity & Expansion Possibilities Analysis
 *
 * This program demonstrates 8 SAS functionalities:
 * 1. Creating SAS datasets from external CSV files (PROC IMPORT)
 * 2. Creating and using user-defined formats (PROC FORMAT)
 * 3. Iterative and conditional processing (DO loops, SELECT-WHEN, IF-THEN-ELSE)
 * 4. Creating data subsets (WHERE, subsetting IF)
 * 5. Using SAS functions (date, string, math functions)
 * 6. Combining datasets (SET, MERGE, PROC SQL)
 * 7. Using arrays
 * 8. Report procedures (PROC PRINT, PROC REPORT, PROC TABULATE)

/


%let DATAPATH = /home/u64485601/BrewNest/data;

/* Create a library reference */
libname brew "&DATAPATH";


/* FUNCTIONALITY 1: Creating SAS Datasets from External Files
   Problem: Import the 5 CSV files into SAS datasets for analysis */
title "FUNCTIONALITY 1: Importing External CSV Files";

proc import datafile="&DATAPATH/stores.csv"
    out=work.stores
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

proc import datafile="&DATAPATH/products.csv"
    out=work.products
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

proc import datafile="&DATAPATH/customers.csv"
    out=work.customers
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

proc import datafile="&DATAPATH/sales.csv"
    out=work.sales
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

proc import datafile="&DATAPATH/employees.csv"
    out=work.employees
    dbms=csv
    replace;
    getnames=yes;
    guessingrows=max;
run;

/* Verify imports */
title2 "Stores Dataset";
proc print data=work.stores(obs=5); run;

title2 "Products Dataset";
proc print data=work.products(obs=5); run;

title2 "Customers Dataset";
proc print data=work.customers(obs=5); run;

title2 "Sales Dataset (first 10 rows)";
proc print data=work.sales(obs=10); run;

title2 "Employees Dataset";
proc print data=work.employees(obs=5); run;
title; title2;


/* FUNCTIONALITY 2: Creating and Using User-Defined Formats
   Problem: Categorize revenue, performance, and regions for
   easier reporting and interpretation */
title "FUNCTIONALITY 2: User-Defined Formats";

proc format;
    /* Revenue category format */
    value revcat
        low -< 10     = 'Low (< 10 RON)'
        10  -< 20     = 'Medium (10-20 RON)'
        20  -< 50     = 'High (20-50 RON)'
        50  - high    = 'Premium (50+ RON)';

    /* Performance score format */
    value perfmt
        low -< 4      = 'Below Average'
        4   -< 6      = 'Average'
        6   -< 8      = 'Good'
        8   - high    = 'Excellent';

    /* Employee salary band format */
    value salaryfmt
        low  -< 3000  = 'Entry Level'
        3000 -< 4500  = 'Junior'
        4500 -< 6000  = 'Mid-Level'
        6000 - high   = 'Senior';

    /* City population size format */
    value popfmt
        low    -< 150000 = 'Small City'
        150000 -< 300000 = 'Medium City'
        300000 - high    = 'Large City';

    /* Discount format */
    value discfmt
        0              = 'No Discount'
        0 < - 0.05     = '5% Discount'
        0.05 < - 0.10  = '10% Discount'
        0.10 < - high  = '15%+ Discount';

    /* Romanian region format (character) */
    value $regfmt
        'Muntenia'      = 'Muntenia (South)'
        'Transilvania'  = 'Transilvania (Central)'
        'Moldova'       = 'Moldova (East)'
        'Banat'         = 'Banat (West)'
        'Dobrogea'      = 'Dobrogea (Southeast)'
        'Oltenia'       = 'Oltenia (Southwest)';
run;

/* Demonstrate format usage */
title2 "Sales with Revenue Categories";
proc print data=work.sales(obs=15);
    format total_revenue revcat. discount discfmt.;
run;

title2 "Employees with Performance and Salary Formats";
proc print data=work.employees(obs=15);
    format performance_score perfmt. salary salaryfmt.;
run;

title2 "Stores with Region and Population Formats";
proc print data=work.stores;
    format region $regfmt. city_population popfmt.;
run;
title; title2;


/* FUNCTIONALITY 3: Iterative and Conditional Processing
   Problem: Create customer tiers based on purchasing behavior
   and calculate cumulative revenue metrics */
title "FUNCTIONALITY 3: Iterative and Conditional Processing";

/* 3a. Customer tiers using SELECT-WHEN (Conditional Processing) */
proc sql;
    create table work.customer_stats as
    select customer_id,
           count(*) as transaction_count,
           sum(total_revenue) as total_spend,
           mean(total_revenue) as avg_basket,
           max(total_revenue) as max_transaction
    from work.sales
    where customer_id is not missing
    group by customer_id;
quit;

data work.customer_tiers;
    set work.customer_stats;

    /* SELECT statement for customer tier classification */
    select;
        when (total_spend >= 500 and transaction_count >= 30) tier = 'Platinum';
        when (total_spend >= 300 and transaction_count >= 20) tier = 'Gold';
        when (total_spend >= 100 and transaction_count >= 10) tier = 'Silver';
        otherwise tier = 'Bronze';
    end;

    /* Conditional loyalty recommendation */
    length recommendation $50;
    if tier = 'Platinum' then recommendation = 'VIP Program + Free Monthly Coffee';
    else if tier = 'Gold' then recommendation = '10% Permanent Discount';
    else if tier = 'Silver' then recommendation = 'Points Multiplier Campaign';
    else recommendation = 'Welcome Offer + First Purchase Bonus';
run;

title2 "Customer Tiers Distribution";
proc freq data=work.customer_tiers;
    tables tier / nocum;
run;

/* 3b. DO loop: Calculate cumulative monthly revenue */
proc sql;
    create table work.monthly_revenue as
    select put(date, yymmn6.) as month_id,
           sum(total_revenue) as monthly_rev
    from work.sales
    group by calculated month_id
    order by calculated month_id;
quit;

data work.cumulative_revenue;
    set work.monthly_revenue;
    retain cumulative_rev 0;
    cumulative_rev + monthly_rev;

    /* Growth rate calculation with DO loop for moving average */
    array prev_months{3} _temporary_;
    retain prev_months1-prev_months3 0;

    /* Shift values in the array */
    do i = 3 to 2 by -1;
        prev_months{i} = prev_months{i-1};
    end;
    prev_months{1} = monthly_rev;

    /* 3-month moving average */
    moving_avg_3m = 0;
    count_valid = 0;
    do j = 1 to 3;
        if prev_months{j} > 0 then do;
            moving_avg_3m + prev_months{j};
            count_valid + 1;
        end;
    end;
    if count_valid > 0 then moving_avg_3m = moving_avg_3m / count_valid;

    drop i j count_valid;
run;

title2 "Cumulative Revenue with 3-Month Moving Average";
proc print data=work.cumulative_revenue(obs=15);
    format monthly_rev cumulative_rev moving_avg_3m comma12.2;
run;




/* FUNCTIONALITY 4: Creating Data Subsets
   Problem: Extract specific segments for targeted analysis */
title "FUNCTIONALITY 4: Data Subsets";

/* 4a. High-revenue transactions (top quartile) */
proc means data=work.sales noprint;
    var total_revenue;
    output out=work.rev_stats q3=q3_revenue;
run;

data work.high_value_sales;
    if _n_ = 1 then set work.rev_stats(keep=q3_revenue);
    set work.sales;
    where total_revenue > 0;
    if total_revenue >= q3_revenue;
run;

title2 "High-Value Sales (Top 25%)";
proc print data=work.high_value_sales(obs=10);
    format total_revenue revcat.;
run;

/* 4b. Bucharest stores only */
data work.bucharest_stores;
    set work.stores;
    where city = 'Bucuresti';
run;

title2 "Bucharest Stores";
proc print data=work.bucharest_stores; run;

/* 4c. Loyal customers with high spending */
data work.vip_customers;
    set work.customers;
    where loyalty_member = 1 and income_bracket = 'High';
run;

title2 "VIP Customers (Loyal + High Income)";
proc print data=work.vip_customers(obs=15); run;

/* 4d. Coffee products only */
data work.coffee_products;
    set work.products;
    where category = 'Coffee';
run;

title2 "Coffee Products";
proc print data=work.coffee_products; run;

/* 4e. Recent employees (hired in 2024) */
data work.new_hires;
    set work.employees;
    where year(hire_date) = 2024;
run;

title2 "Employees Hired in 2024";
proc print data=work.new_hires; run;
title; title2;


/* FUNCTIONALITY 5: Using SAS Functions
   Problem: Derive new business metrics using date, string,
   and mathematical functions */
title "FUNCTIONALITY 5: SAS Functions";

data work.stores_enhanced;
    set work.stores;

    /* Date functions */
    open_date = opening_date;
    today = today();
    months_open = intck('month', open_date, today);
    years_open = intck('year', open_date, today);

    /* String functions */
    city_upper = upcase(city);
    city_length = length(city);
    store_label = catx(' - ', store_id, city, region);

    /* Mathematical functions */
    rent_per_sqm = round(monthly_rent / size_sqm, 0.01);
    annual_rent = monthly_rent * 12;
    log_population = round(log(city_population), 0.01);
    revenue_per_emp = round(monthly_rent / employee_count, 0.01);

    /* Conditional function */
    store_size_cat = ifc(size_sqm >= 150, 'Large Store', 
                    ifc(size_sqm >= 80, 'Medium Store', 'Small Store'));

    format open_date today date9. annual_rent comma10.;
run;

title2 "Enhanced Store Data with Derived Metrics";
proc print data=work.stores_enhanced;
    var store_id city months_open rent_per_sqm annual_rent
        log_population store_size_cat store_label;
run;
title; title2;


/* FUNCTIONALITY 6: Combining Datasets (MERGE + PROC SQL)
   Problem: Create unified views by joining sales with store,
   product, and customer information */
title "FUNCTIONALITY 6: Combining Datasets";

/* 6a. MERGE - Sales with Stores (requires sorting first) */
proc sort data=work.sales out=work.sales_sorted;
    by store_id;
run;

proc sort data=work.stores out=work.stores_sorted;
    by store_id;
run;

data work.sales_stores;
    merge work.sales_sorted(in=a) work.stores_sorted(in=b);
    by store_id;
    if a and b;
run;

title2 "6a. Sales + Stores (MERGE)";
proc print data=work.sales_stores(obs=10);
    var transaction_id store_id city region date total_revenue;
run;

/* 6b. PROC SQL - Full transaction view (multi-table join) */
proc sql;
    create table work.full_transactions as
    select s.transaction_id,
           s.store_id,
           st.city,
           st.region,
           s.product_id,
           p.name as product_name,
           p.category,
           s.customer_id,
           s.date,
           s.quantity,
           s.total_revenue,
           p.cost_price,
           (s.total_revenue - (p.cost_price * s.quantity)) as profit
    from work.sales s
    inner join work.stores st on s.store_id = st.store_id
    inner join work.products p on s.product_id = p.product_id
    order by s.date desc;
quit;

title2 "6b. Full Transaction View (PROC SQL Join)";
proc print data=work.full_transactions(obs=15);
    format total_revenue profit comma10.2;
run;

/* 6c. Concatenating Datasets using SET and DATALINES */
data work.new_stores_north;
    input store_id $ city $ region $;
datalines;
S101 Suceava Moldova
S102 Botosani Moldova
;
run;

data work.new_stores_south;
    input store_id $ city $ region $;
datalines;
S103 Giurgiu Muntenia
S104 Calarasi Muntenia
;
run;

data work.all_new_stores;
    set work.new_stores_north work.new_stores_south;
run;

title2 "6c. Concatenated Data Sets (SET)";
proc print data=work.all_new_stores;
run;

/* 6d. SQL Aggregation - Revenue by city and category */
proc sql;
    create table work.city_category_rev as
    select st.city,
           p.category,
           count(*) as transactions,
           sum(s.total_revenue) as total_revenue,
           mean(s.total_revenue) as avg_transaction
    from work.sales s
    inner join work.stores st on s.store_id = st.store_id
    inner join work.products p on s.product_id = p.product_id
    group by st.city, p.category
    order by st.city, total_revenue desc;
quit;

title2 "6c. Revenue by City and Product Category";
proc print data=work.city_category_rev(obs=20);
    format total_revenue avg_transaction comma10.2;
run;
title; title2;


/* FUNCTIONALITY 7: Using Arrays
   Problem: Calculate monthly revenue distribution per store
   and standardize numeric scores */
title "FUNCTIONALITY 7: Arrays";

/* 7a. Monthly revenue by store using arrays */
proc sql;
    create table work.store_monthly_raw as
    select store_id,
           month(date) as sale_month,
           sum(total_revenue) as monthly_rev
    from work.sales
    group by store_id, calculated sale_month
    order by store_id, sale_month;
quit;

/* Pivot using arrays */
data work.store_monthly_pivot;
    array month_rev{12} Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec;
    retain Jan--Dec 0;

    set work.store_monthly_raw;
    by store_id;

    if first.store_id then do;
        do i = 1 to 12;
            month_rev{i} = 0;
        end;
    end;

    month_rev{sale_month} + monthly_rev;

    if last.store_id then do;
        /* Calculate annual total and best/worst months */
        annual_total = 0;
        best_month = 1;
        worst_month = 1;
        do i = 1 to 12;
            annual_total + month_rev{i};
            if month_rev{i} > month_rev{best_month} then best_month = i;
            if month_rev{i} < month_rev{worst_month} and month_rev{i} > 0 then worst_month = i;
        end;
        output;
    end;

    drop i sale_month monthly_rev;
    format Jan--Dec annual_total comma10.2;
run;

title2 "7a. Monthly Revenue Pivot per Store";
proc print data=work.store_monthly_pivot;
    var store_id Jan--Dec annual_total best_month worst_month;
run;

/* 7b. Standardize employee scores using arrays */
data work.emp_standardized;
    set work.employees;

    /* Array of numeric score columns */
    array scores{2} performance_score satisfaction_score;
    array std_scores{2} perf_std satis_std;

    /* Manual standardization (for demonstration) */
    /* Approximate means and stds from the data */
    array means{2} _temporary_ (6.5 6.0);
    array stds{2} _temporary_ (2.0 2.3);

    do k = 1 to 2;
        if scores{k} ne . then
            std_scores{k} = round((scores{k} - means{k}) / stds{k}, 0.01);
        else
            std_scores{k} = .;
    end;

    drop k;
run;

title2 "7b. Standardized Employee Scores";
proc print data=work.emp_standardized(obs=15);
    var employee_id name role performance_score perf_std
        satisfaction_score satis_std;
run;
title; title2;


/* FUNCTIONALITY 8: Report Procedures
   Problem: Generate professional management reports */
title "FUNCTIONALITY 8: Report Procedures";

/* 8a. PROC REPORT - Store Performance Report */
title2 "8a. Store Performance Report";
proc report data=work.full_transactions nowd;
    column city store_id total_revenue profit quantity;
    define city / group 'City';
    define store_id / group 'Store';
    define total_revenue / analysis sum 'Total Revenue' format=comma12.2;
    define profit / analysis sum 'Total Profit' format=comma12.2;
    define quantity / analysis sum 'Units Sold' format=comma10.;

    rbreak after / summarize;
    compute after;
        city = 'GRAND TOTAL';
    endcomp;
run;

/* 8b. PROC TABULATE - Product Category Analysis */
title2 "8b. Product Performance by Category and Region";
proc tabulate data=work.full_transactions;
    class category region;
    var total_revenue quantity profit;
    table category all='TOTAL',
          region*(total_revenue*sum quantity*sum) /
          box='Category x Region';
    format total_revenue comma10. quantity comma8. profit comma10.;
run;

/* 8c. PROC REPORT with computed columns */
title2 "8c. Employee Summary Report with Computed Columns";
proc report data=work.employees nowd;
    column store_id role salary performance_score satisfaction_score composite;
    define store_id / group 'Store';
    define role / group 'Role';
    define salary / analysis mean 'Avg Salary' format=comma10.;
    define performance_score / analysis mean 'Avg Performance' format=5.1;
    define satisfaction_score / analysis mean 'Avg Satisfaction' format=5.1;
    define composite / computed 'Composite Score' format=5.2;

    compute composite;
        composite = performance_score.mean * 0.6 + satisfaction_score.mean * 0.4;
    endcomp;
run;
title; title2;