import org.rogach.scallop.{ScallopConf, ScallopOption}

class SatelliteETLConf(arguments: Seq[String]) extends ScallopConf(arguments) {
  val inpath: ScallopOption[String] = opt[String] (default = Some("H:\\"))
  val outpath: ScallopOption[String] = opt[String] (default = Some("H:\\"))
  val files: ScallopOption[String] = opt[String] (default = Some("B2,B3"))

  verify()
}
