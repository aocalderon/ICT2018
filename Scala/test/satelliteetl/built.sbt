name := "SatelliteETL"
organization := "USC-ICT"
version := "0.1"

scalaVersion := "2.11.8"

libraryDependencies += "org.apache.spark" %% "spark-sql" % "2.1.0"
libraryDependencies += "joda-time" % "joda-time" % "2.9.9"
libraryDependencies += "org.joda" % "joda-convert" % "1.8.1"
libraryDependencies += "org.slf4j" % "slf4j-jdk14" % "1.7.25"
libraryDependencies += "org.rogach" % "scallop_2.11" % "2.1.3"

mainClass in (Compile, run) := Some("edu.usc.ict.SatelliteETL")
mainClass in (Compile, packageBin) := Some("edu.usc.ict.SatelliteETL")
