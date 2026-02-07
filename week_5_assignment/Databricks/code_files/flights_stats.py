from pyspark import pipelines as dp
from pyspark.sql.functions import *
 
@dp.table
def flights_stats():
    df = spark.read.table("ingest_flights")  # Ensure the table is materialized
    return(
        df.agg(
            count("*").alias("num_events"),
            countDistinct("icao24").alias("distinct_aircraft"),
            max("velocity").alias("max_velocity"),
        )
    )