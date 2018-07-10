package edu.usc.ict

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types.StructType
import org.apache.spark.sql.catalyst.ScalaReflection
import org.slf4j.{Logger, LoggerFactory}
import org.rogach.scallop.{ScallopConf, ScallopOption}

object DatasetWriter {
  case class Pixel(x: Double, y: Double, value: Integer)
  case class PixelValues(x: Double, y: Double, values: String)
  private val logger: Logger = LoggerFactory.getLogger("myLogger")

  def main(args: Array[String]) {
    logger.info("Setting variables...")
    val pixelSchema = ScalaReflection.schemaFor[Pixel].dataType.asInstanceOf[StructType]
    val inpath = "H:\\data\\"
    val images = "B2,B3,B4,B5"

    logger.info("Starting session...")
    val spark = SparkSession.builder
      .master("local[*]")
      .appName("DatasetWriter")
      .getOrCreate()
    import spark.implicits._
    var dataset = spark.sparkContext.emptyRDD[PixelValues].toDS()
    var nDataset = 0L

    for(image <- images.split(",")){
      logger.info(s"Reading band ${image}...")
      val band = spark.read.parquet(s"${inpath}${image}").as[Pixel].cache()
      val nBand = band.count()
      band.show()
      logger.info(s"Number of records: $nBand")
      if(nDataset == 0L){
        dataset = band.map(p => PixelValues(p.x, p.y, s"${p.value}")).cache()
        nDataset = nBand
      } else {
        dataset = dataset.as("left").join(band.as("right"), $"left.x" === $"right.x" && $"left.y" === $"right.y")
          .select($"left.x", $"left.y", $"left.values", $"right.value")
          .map{ p =>
            val x = p.getDouble(0)
            val y = p.getDouble(1)
            val vLeft  = p.getString(2)
            val vRight = p.getInt(3)

            PixelValues(x, y, s"$vLeft,$vRight")
          }.cache
        nDataset = dataset.count()
      }
    }
    dataset.show()
    logger.info(s"Total number of records: $nDataset")

    logger.info("Closing session...")
    spark.close()
  }
}
