--
-- PostgreSQL database dump
--

\restrict t3GCFneuoniaT0WFBwdGsIeqZhU3eV5rWTWmBpq9llFdiALZQ4La8XhfQOP5GhG

-- Dumped from database version 14.17
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


--
-- Name: register_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.register_type AS ENUM (
    'CONSUMPTION_PEAK',
    'CONSUMPTION_OFFPEAK',
    'INJECTION_PEAK',
    'INJECTION_OFFPEAK'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: measures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.measures (
    read_at timestamp with time zone NOT NULL,
    register public.register_type NOT NULL,
    volume_kwh numeric(10,4) NOT NULL,
    calculated_power_kw numeric(10,4) GENERATED ALWAYS AS ((volume_kwh * (4)::numeric)) STORED,
    is_valid boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: measures measures_unique_read_register; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.measures
    ADD CONSTRAINT measures_unique_read_register UNIQUE (read_at, register);


--
-- Name: measures_read_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX measures_read_at_idx ON public.measures USING btree (read_at DESC);


--
-- Name: measures ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.measures FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- PostgreSQL database dump complete
--

\unrestrict t3GCFneuoniaT0WFBwdGsIeqZhU3eV5rWTWmBpq9llFdiALZQ4La8XhfQOP5GhG

