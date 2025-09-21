
---------------------

# "public" schema for Neural Capital AI

`This is not final yet, still in brainstorming phase`

## In Supabase (PostgreSQL)

---------------------

### users
- **id**: bigint
- **created_at**: timestamp with time zone
- **email**: text
- **id_alpaca**: text
- **city**: text
- **contact_email**: text
- **contact_family**: text
- **contact_given**: text
- **country_of_birth**: text
- **country_of_citizenship**: text
- **date_of_birth**: date
- **family_name**: text
- **given_name**: text
- **phone**: double precision
- **postal_code**: bigint
- **state**: text
- **street_address**: text
- **tax_id**: bigint
- **id_user**: uuid
- **user_tier**: text

---
### agent_transactions
- **transactionid**: uuid
- **agentid**: uuid
- **userid**: uuid
- **timestamp**: timestamp with time zone
- **inputdata**: jsonb
- **outputdata**: jsonb
- **costinsolana**: numeric(10, 6)
- **solanatxnhash**: text

---
### agents
- **agentid**: uuid
- **agentname**: text
- **description**: text
- **api_endpoint**: text
- **pricingmodel**: text
- **costperunit**: numeric(10, 6)
- **ownerwalletaddress**: text
- **isrentable**: boolean

---
### ai_insights
- **id**: uuid
- **session_id**: uuid
- **user_id**: text
- **insight_type**: text
- **insight_text**: text
- **confidence_score**: numeric(3, 2)
- **metadata**: jsonb
- **created_at**: timestamp with time zone

---
### analysis_sessions
- **id**: uuid
- **user_id**: character varying(255)
- **goal_text**: text
- **session_type**: character varying(50)
- **status**: character varying(20)
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone

---
### assets
- **assetid**: uuid
- **ticker**: text
- **assetname**: text
- **assettype**: text
- **isoptional**: boolean
- **description**: text

---
### dashboard_macro_data
- **id**: serial
- **indicator_code**: character varying(50)
- **indicator_name**: character varying(255)
- **value**: numeric(15, 4)
- **date**: date
- **frequency**: character varying(20)
- **units**: character varying(100)
- **source**: character varying(50)
- **category**: character varying(100)
- **subcategory**: character varying(100)
- **seasonally_adjusted**: boolean
- **revision_date**: timestamp without time zone
- **metadata**: jsonb
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone

---
### dashboard_market_data
- **id**: uuid
- **symbol**: character varying(10)
- **name**: character varying(100)
- **asset_type**: character varying(20)
- **price**: numeric(12, 4)
- **previous_close**: numeric(12, 4)
- **change_value**: numeric(12, 4)
- **change_percent**: numeric(8, 4)
- **volume**: bigint
- **market_cap**: bigint
- **pe_ratio**: numeric(8, 2)
- **dividend_yield**: numeric(6, 4)
- **day_high**: numeric(12, 4)
- **day_low**: numeric(12, 4)
- **year_high**: numeric(12, 4)
- **year_low**: numeric(12, 4)
- **expense_ratio**: numeric(6, 4)
- **total_assets**: bigint
- **beta**: numeric(6, 3)
- **sma_20**: numeric(12, 4)
- **sma_50**: numeric(12, 4)
- **sma_200**: numeric(12, 4)
- **rsi**: numeric(6, 2)
- **context_data**: jsonb
- **data_timestamp**: timestamp with time zone
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone

---
### explainability_analysis
- **id**: uuid
- **recommendation_id**: uuid
- **agent_type**: character varying(50)
- **original_query**: text
- **recommendation_summary**: text
- **explanation_text**: text
- **confidence_score**: numeric(5, 4)
- **reasoning_steps**: jsonb
- **risk_factors**: jsonb
- **assumptions**: jsonb
- **alternative_scenarios**: jsonb
- **data_sources**: jsonb
- **methodology**: character varying(100)
- **limitations**: text
- **user_feedback**: jsonb
- **follow_up_questions**: jsonb
- **complexity_level**: character varying(20)
- **explanation_type**: character varying(50)
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone
- **session_id**: uuid
- **user_id**: text
- **main_explanation**: text
- **risk_framework**: text
- **return_expectations**: text
- **monitoring_approach**: text
- **word_count**: integer
- **theoretical_framework**: text
- **explanation_metadata**: text
- **explanation_summary**: jsonb
- **components**: jsonb
- **quality_metrics**: jsonb

---
### investment_plans
- **id**: uuid
- **user_id**: uuid
- **financial_goals**: text
- **investment_preferences**: text
- **plan_data**: jsonb
- **plan_name**: character varying(255)
- **plan_type**: character varying(50)
- **risk_level**: character varying(20)
- **time_horizon**: integer
- **target_amount**: numeric(15, 2)
- **agent_2_data**: jsonb
- **agent_3_data**: jsonb
- **processing_status**: character varying(20)
- **is_active**: boolean
- **is_favorite**: boolean
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone
- **last_reviewed_at**: timestamp with time zone
- **expected_return**: numeric(8, 4)
- **actual_return**: numeric(8, 4)
- **performance_notes**: text

---
### market_events
- **eventid**: uuid
- **eventname**: text
- **startdate**: date
- **enddate**: date
- **description**: text

---
### market_time_series
- **datapointid**: uuid
- **date**: timestamp without time zone
- **assetid**: uuid
- **metricname**: text
- **value**: numeric
- **datasource**: text

---
### monte_carlo_results
- **id**: uuid
- **planner_id**: uuid
- **scenario**: character varying(50)
- **success_probability**: numeric(4, 3)
- **expected_final_value**: numeric(15, 2)
- **percentile_10**: numeric(15, 2)
- **percentile_50**: numeric(15, 2)
- **percentile_90**: numeric(15, 2)
- **shortfall_risk**: numeric(4, 3)
- **excess_probability**: numeric(4, 3)
- **required_monthly_savings**: numeric(10, 2)
- **confidence_interval_lower**: numeric(15, 2)
- **confidence_interval_upper**: numeric(15, 2)
- **created_at**: timestamp with time zone

---
### planner_analysis
- **id**: uuid
- **session_id**: uuid
- **user_id**: character varying(255)
- **goal_type**: character varying(50)
- **target_amount**: numeric(15, 2)
- **time_horizon_years**: integer
- **current_age**: integer
- **risk_tolerance**: character varying(50)
- **monthly_investment**: numeric(10, 2)
- **success_probability**: numeric(4, 3)
- **expected_final_value**: numeric(15, 2)
- **goal_summary**: text
- **asset_allocation**: jsonb
- **risk_considerations**: jsonb
- **milestones**: jsonb
- **alternative_scenarios**: jsonb
- **stress_test_summary**: text
- **created_at**: timestamp with time zone

---
### planner_rules
- **ruleid**: uuid
- **rulename**: text
- **ruletype**: text
- **conditions**: jsonb
- **actionallocations**: jsonb
- **explanationtemplate**: text

---
### portfolio_analysis
- **id**: uuid
- **session_id**: uuid
- **user_id**: character varying(255)
- **risk_level**: integer
- **allocations**: jsonb
- **expected_return**: numeric(5, 4)
- **expected_risk**: numeric(5, 4)
- **sharpe_ratio**: numeric(6, 4)
- **portfolio_value**: numeric(15, 2)
- **created_at**: timestamp with time zone

---
### portfolio_performance_metrics
- **performancerecordid**: uuid
- **userportfolioid**: uuid
- **date**: date
- **sharperatio**: numeric(5, 2)
- **sortinoratio**: numeric(5, 2)
- **maxdrawdown**: numeric(5, 2)
- **turnover**: numeric(5, 2)
- **winrate**: numeric(5, 2)
- **informationratio**: numeric(5, 2)
- **cagr**: numeric(5, 2)
- **volatility**: numeric(5, 2)
- **returnduringcrash**: numeric(5, 2)
- **recoverytimedays**: integer

---
### rebalancing_triggers
- **id**: uuid
- **portfolio_id**: uuid
- **trigger_name**: character varying(100)
- **condition_met**: boolean
- **trigger_value**: numeric(8, 6)
- **threshold**: numeric(8, 6)
- **confidence**: numeric(4, 3)
- **urgency**: character varying(20)
- **recommended_action**: text
- **expected_impact**: numeric(6, 4)
- **created_at**: timestamp with time zone

---
### recommendation_explanations
- **id**: uuid
- **session_id**: uuid
- **user_id**: text
- **recommendation_type**: text
- **explanation_text**: text
- **rationale**: text
- **metadata**: jsonb
- **created_at**: timestamp with time zone

---
### risk_tiers
- **risktierid**: integer
- **riskname**: text
- **profiledescription**: text
- **investmenthorizon**: text
- **expectedreturn**: numeric(5, 4)
- **volatility**: numeric(5, 4)
- **sharperatio**: numeric(5, 2)
- **targetallocations**: jsonb

---
### signal_rules
- **signalid**: uuid
- **signalname**: text
- **description**: text
- **frequency**: text
- **conditiontrigger**: jsonb
- **action**: jsonb
- **applicablerisktiers**: text
- **cooldownperioddays**: integer
- **reversalcondition**: jsonb

---
### stress_tests
- **id**: uuid
- **portfolio_id**: uuid
- **scenario**: character varying(50)
- **portfolio_loss**: numeric(6, 4)
- **worst_asset_loss**: numeric(6, 4)
- **recovery_time_estimate**: integer
- **risk_adjusted_return**: numeric(6, 4)
- **max_drawdown**: numeric(6, 4)
- **var_95**: numeric(6, 4)
- **expected_shortfall**: numeric(6, 4)
- **stress_ratio**: numeric(6, 4)
- **created_at**: timestamp with time zone

---
### transaction_logs
- **logid**: uuid
- **userportfolioid**: uuid
- **timestamp**: timestamp with time zone
- **actiontype**: text
- **assetid**: uuid
- **quantity**: numeric(15, 6)
- **price**: numeric(10, 2)
- **amount**: numeric(12, 2)
- **reason**: text
- **signalid**: uuid
- **issimulated**: boolean
- **alpacaorderid**: text

---
### user_dashboard_settings
- **id**: uuid
- **user_id**: uuid
- **watchlist_symbols**: text[]
- **preferred_charts**: jsonb
- **refresh_interval**: integer
- **theme**: character varying(20)
- **layout_config**: jsonb
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone

---
### user_goals
- **goalid**: uuid
- **userid**: uuid
- **goaldescription**: text
- **goaltype**: text
- **targetamount**: numeric(12, 2)
- **targetdate**: date
- **currentsavings**: numeric(12, 2)
- **assignedrisktierid**: integer
- **experience**: text

---
### user_portfolio_holdings
- **holdingid**: uuid
- **userportfolioid**: uuid
- **assetid**: uuid
- **currentallocationpercentage**: numeric(5, 2)
- **targetallocationpercentage**: numeric(5, 2)
- **numberofunits**: numeric(15, 6)
- **averagecostbasis**: numeric(10, 2)
- **currentvalue**: numeric(12, 2)

---
### user_portfolios
- **userportfolioid**: uuid
- **userid**: uuid
- **goalid**: uuid
- **portfolioname**: text
- **currentrisktierid**: integer
- **creationdate**: date
- **lastrebalancedate**: date
- **currenttotalvalue**: numeric(12, 2)

---
### user_preferences
- **preferences_id**: uuid
- **user_id**: uuid
- **primary_goal**: text
- **investment_horizon**: text
- **experience_level**: text
- **risk_tolerance**: integer
- **starting_amount**: numeric
- **monthly_contribution**: numeric
- **assets_to_avoid**: jsonb
- **comfortable_assets**: jsonb
- **auto_pay_amount**: numeric
- **auto_pay_cadence**: text
- **auto_pay_to_savings**: text
- **budget_guardrail**: integer
- **concentration_cap**: integer
- **consent_to_automation**: boolean
- **contribution_day**: integer
- **create_auto_split**: text
- **dca_cadence**: text
- **equity_stop_loss**: integer
- **equity_take_profit**: integer
- **margin_allowed**: boolean
- **max_drawdown**: integer
- **portfolio_drawdown_alert**: integer
- **rebalancing**: text
- **sector_caps**: jsonb
- **split_recipe**: jsonb
- **state_of_residence**: text
- **tax_wrapper**: text
- **created_at**: timestamp with time zone
- **updated_at**: timestamp with time zone
