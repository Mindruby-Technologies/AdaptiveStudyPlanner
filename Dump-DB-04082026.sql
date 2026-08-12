-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: adaptive_study_planner
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ai_mocktest_reports`
--

DROP TABLE IF EXISTS `ai_mocktest_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_mocktest_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` bigint NOT NULL,
  `student_name` varchar(255) DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `test_name` varchar(255) DEFAULT NULL,
  `test_date` date DEFAULT NULL,
  `total_score` varchar(50) DEFAULT NULL,
  `score_range` varchar(50) DEFAULT NULL,
  `percentile` varchar(50) DEFAULT NULL,
  `extracted_json` json DEFAULT NULL,
  `ai_report` json DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `uploaded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','processed') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  KEY `test_id` (`test_id`),
  CONSTRAINT `ai_mocktest_reports_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ai_mocktest_reports`
--

LOCK TABLES `ai_mocktest_reports` WRITE;
/*!40000 ALTER TABLE `ai_mocktest_reports` DISABLE KEYS */;
INSERT INTO `ai_mocktest_reports` VALUES (1,1,'Aditi Danani',NULL,'SAT Practice 4','2025-11-05','1460','400-1600',NULL,'{\"grade\": null, \"test_date\": \"2025-11-05\", \"test_name\": \"SAT Practice 4\", \"percentile\": null, \"score_range\": \"400-1600\", \"total_score\": 1460, \"student_name\": \"Aditi Danani\", \"section_scores\": [{\"range\": \"200-800\", \"score\": 770, \"section\": \"Reading and Writing\", \"percentile\": null}, {\"range\": \"200-800\", \"score\": 690, \"section\": \"Math\", \"percentile\": null}], \"knowledge_areas\": [{\"topic\": \"Information and Ideas\", \"max_marks\": null, \"percentage\": 26, \"marks_obtained\": null}, {\"topic\": \"Expression of Ideas\", \"max_marks\": null, \"percentage\": 20, \"marks_obtained\": null}, {\"topic\": \"Craft and Structure\", \"max_marks\": null, \"percentage\": 28, \"marks_obtained\": null}, {\"topic\": \"Standard English Conventions\", \"max_marks\": null, \"percentage\": 26, \"marks_obtained\": null}, {\"topic\": \"Algebra\", \"max_marks\": null, \"percentage\": 35, \"marks_obtained\": null}, {\"topic\": \"Advanced Math\", \"max_marks\": null, \"percentage\": 35, \"marks_obtained\": null}, {\"topic\": \"Problem-Solving and Data Analysis\", \"max_marks\": null, \"percentage\": 15, \"marks_obtained\": null}, {\"topic\": \"Geometry and Trigonometry\", \"max_marks\": null, \"percentage\": 15, \"marks_obtained\": null}]}','{\"strengths\": [\"Outstanding performance in the Reading and Writing section (770/800).\", \"Strong understanding of Craft and Structure (28%) within Reading and Writing.\", \"Good grasp of Information and Ideas (26%) and Standard English Conventions (26%) in Reading and Writing.\"], \"weaknesses\": [\"Lower relative performance in the Math section (690/800) compared to Reading and Writing.\", \"Significant weakness in Problem-Solving and Data Analysis (15%) within Math.\", \"Significant weakness in Geometry and Trigonometry (15%) within Math.\", \"Expression of Ideas (20%) is a relative area for improvement within Reading and Writing.\"], \"focus_areas\": [\"Problem-Solving and Data Analysis\", \"Geometry and Trigonometry\", \"Expression of Ideas\"], \"trend_summary\": \"No previous records are available for comparison, so a trend analysis (improvement or decline) cannot be performed at this time.\", \"topic_insights\": [{\"note\": \"Solid performance within Reading and Writing, indicating good comprehension skills. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Information and Ideas\", \"status\": null}, {\"note\": \"This is a relative area of weakness within Reading and Writing, suggesting a need to focus on organization, rhetoric, and effective communication. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Expression of Ideas\", \"status\": null}, {\"note\": \"Strongest performance within Reading and Writing, demonstrating proficiency in understanding text structure and author\'s craft. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Craft and Structure\", \"status\": null}, {\"note\": \"Good performance in grammar and usage, contributing well to the Reading and Writing score. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Standard English Conventions\", \"status\": null}, {\"note\": \"A foundational area in Math with a decent score, but opportunities exist for further mastery. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Algebra\", \"status\": null}, {\"note\": \"Similar to Algebra, performance is adequate but not a top strength, indicating room for deeper understanding. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Advanced Math\", \"status\": null}, {\"note\": \"A significant area of weakness in Math, requiring focused practice on interpreting data and solving complex problems. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Problem-Solving and Data Analysis\", \"status\": null}, {\"note\": \"Another significant area of weakness in Math, suggesting a need for foundational review and advanced concepts. (Trend cannot be determined due to lack of historical data.)\", \"topic\": \"Geometry and Trigonometry\", \"status\": null}], \"overall_summary\": \"Aditi Danani achieved a strong total score of 1460 on the SAT Practice 4 test. Her performance was exceptional in the Reading and Writing section, while the Math section, though good, presents the primary opportunity for score improvement.\", \"recommendations\": [\"Prioritize dedicated study and practice for Math, particularly focusing on Problem-Solving and Data Analysis, and Geometry and Trigonometry.\", \"Review foundational concepts and advanced problem types in both identified weak Math areas.\", \"Work on improving skills related to Expression of Ideas within the Reading and Writing section, focusing on organization, style, and rhetoric.\", \"Consider timed practice sessions for Math to build speed and accuracy in weaker areas.\"], \"section_analysis\": [{\"section\": \"Reading and Writing\", \"analysis\": \"Aditi\'s score of 770 in Reading and Writing is excellent, indicating a very strong command of the verbal sections of the SAT. While overall strong, Expression of Ideas (20%) stands out as a minor area for refinement to achieve an even higher score.\"}, {\"section\": \"Math\", \"analysis\": \"The Math score of 690 is good but presents the largest opportunity for overall score improvement. While Algebra and Advanced Math show decent performance, Problem-Solving and Data Analysis, and Geometry and Trigonometry are clear areas needing focused attention.\"}]}','ADANANI_SAT_PRACTICE_4_11052025.pdf','2026-07-29 12:07:39','processed'),(2,1,'Aditi Danani',NULL,'SAT Practice 11','2026-06-05','1560','400-1600',NULL,'{\"grade\": null, \"test_date\": \"2026-06-05\", \"test_name\": \"SAT Practice 11\", \"percentile\": null, \"score_range\": \"400-1600\", \"total_score\": 1560, \"student_name\": \"Aditi Danani\", \"section_scores\": [{\"range\": \"200-800\", \"score\": 760, \"section\": \"Reading and Writing\", \"percentile\": null}, {\"range\": \"200-800\", \"score\": 800, \"section\": \"Math\", \"percentile\": null}], \"knowledge_areas\": [{\"topic\": \"Information and Ideas\", \"max_marks\": null, \"percentage\": 26, \"marks_obtained\": null}, {\"topic\": \"Expression of Ideas\", \"max_marks\": null, \"percentage\": 20, \"marks_obtained\": null}, {\"topic\": \"Craft and Structure\", \"max_marks\": null, \"percentage\": 28, \"marks_obtained\": null}, {\"topic\": \"Standard English Conventions\", \"max_marks\": null, \"percentage\": 26, \"marks_obtained\": null}, {\"topic\": \"Algebra\", \"max_marks\": null, \"percentage\": 35, \"marks_obtained\": null}, {\"topic\": \"Advanced Math\", \"max_marks\": null, \"percentage\": 35, \"marks_obtained\": null}, {\"topic\": \"Problem-Solving and Data Analysis\", \"max_marks\": null, \"percentage\": 15, \"marks_obtained\": null}, {\"topic\": \"Geometry and Trigonometry\", \"max_marks\": null, \"percentage\": 15, \"marks_obtained\": null}]}','{\"strengths\": [\"Perfect score in Math (800)\", \"Outstanding performance in Reading and Writing (760)\", \"Strong overall improvement trend across tests\", \"High level of mastery in all SAT subjects\"], \"weaknesses\": [\"No significant weaknesses are identifiable from the provided data given the high scores. Minor areas for perfection might exist within the Reading and Writing section.\"], \"focus_areas\": [\"Refining Reading and Writing skills to minimize any remaining errors and aim for a perfect score.\"], \"trend_summary\": \"Aditi\'s performance shows a remarkable upward trend. Comparing SAT Practice 11 (1560) to SAT Practice 4 (1460), she has achieved a substantial 100-point increase in her total score. This improvement is primarily attributed to an outstanding 110-point gain in the Math section, where she moved from 690 to a perfect 800. The Reading and Writing section maintained an exceptionally high level of performance, experiencing only a minor dip of 10 points (from 770 to 760) but remaining near perfect.\", \"topic_insights\": [{\"note\": \"Performance in this area is inferred as very strong given the high Reading and Writing section score (760), likely stable with minimal room for improvement.\", \"topic\": \"Information and Ideas\", \"status\": \"stable\"}, {\"note\": \"Performance in this area is inferred as very strong given the high Reading and Writing section score (760), likely stable with minimal room for improvement.\", \"topic\": \"Expression of Ideas\", \"status\": \"stable\"}, {\"note\": \"Performance in this area is inferred as very strong given the high Reading and Writing section score (760), likely stable with minimal room for improvement.\", \"topic\": \"Craft and Structure\", \"status\": \"stable\"}, {\"note\": \"Performance in this area is inferred as very strong given the high Reading and Writing section score (760), likely stable with minimal room for improvement.\", \"topic\": \"Standard English Conventions\", \"status\": \"stable\"}, {\"note\": \"Performance is exceptional, reflecting the perfect Math score and significant improvement in the section. Mastery demonstrated.\", \"topic\": \"Algebra\", \"status\": \"improving\"}, {\"note\": \"Performance is exceptional, reflecting the perfect Math score and significant improvement in the section. Mastery demonstrated.\", \"topic\": \"Advanced Math\", \"status\": \"improving\"}, {\"note\": \"Performance is exceptional, reflecting the perfect Math score and significant improvement in the section. Mastery demonstrated.\", \"topic\": \"Problem-Solving and Data Analysis\", \"status\": \"improving\"}, {\"note\": \"Performance is exceptional, reflecting the perfect Math score and significant improvement in the section. Mastery demonstrated.\", \"topic\": \"Geometry and Trigonometry\", \"status\": \"improving\"}], \"overall_summary\": \"Aditi Danani has demonstrated exceptional performance on SAT Practice 11, achieving a total score of 1560. This represents a significant improvement from her previous attempt, driven by a perfect score in Math and near-perfect performance in Reading and Writing.\", \"recommendations\": [\"Continue consistent practice to maintain the current high level of performance.\", \"Review any specific questions missed in the Reading and Writing section to pinpoint and refine the most minor areas, aiming for a perfect 1600.\", \"Consider taking the actual SAT soon, as current performance indicates strong readiness.\", \"Focus on test-taking strategies to manage time effectively and avoid careless errors.\"], \"section_analysis\": [{\"section\": \"Reading and Writing\", \"analysis\": \"Aditi scored an outstanding 760 in Reading and Writing. While this is a slight decrease of 10 points from her previous score of 770, it remains an exceptionally high score, demonstrating robust proficiency across all sub-areas of the section. Further analysis of question types missed could help achieve a perfect 800.\"}, {\"section\": \"Math\", \"analysis\": \"Aditi achieved a perfect score of 800 in Math, representing a significant 110-point improvement from her previous score of 690. This indicates complete mastery of all mathematical concepts tested, including Algebra, Advanced Math, Problem-Solving and Data Analysis, and Geometry and Trigonometry.\"}]}','ADANANI_SAT_PRACTICE_11_06052026.pdf','2026-07-29 12:10:04','processed');
/*!40000 ALTER TABLE `ai_mocktest_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mocktest_topics`
--

DROP TABLE IF EXISTS `mocktest_topics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mocktest_topics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mocktest_id` int NOT NULL,
  `topic_id` bigint NOT NULL,
  `marks_obtained` decimal(6,2) NOT NULL DEFAULT '0.00',
  `max_marks` decimal(6,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `mocktest_id` (`mocktest_id`),
  KEY `topic_id` (`topic_id`),
  CONSTRAINT `mocktest_topics_ibfk_1` FOREIGN KEY (`mocktest_id`) REFERENCES `mocktests` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mocktest_topics_ibfk_2` FOREIGN KEY (`topic_id`) REFERENCES `topics` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mocktest_topics`
--

LOCK TABLES `mocktest_topics` WRITE;
/*!40000 ALTER TABLE `mocktest_topics` DISABLE KEYS */;
/*!40000 ALTER TABLE `mocktest_topics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mocktests`
--

DROP TABLE IF EXISTS `mocktests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mocktests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `test_date` date NOT NULL,
  `test_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `test_id` (`test_id`),
  CONSTRAINT `mocktests_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mocktests`
--

LOCK TABLES `mocktests` WRITE;
/*!40000 ALTER TABLE `mocktests` DISABLE KEYS */;
/*!40000 ALTER TABLE `mocktests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_entries`
--

DROP TABLE IF EXISTS `schedule_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_entries` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `topic_id` bigint NOT NULL,
  `schedule_date` date NOT NULL,
  `allocated_hours` decimal(5,2) DEFAULT NULL,
  `missed` enum('yes','no') DEFAULT 'no',
  PRIMARY KEY (`id`),
  KEY `topic_id` (`topic_id`),
  CONSTRAINT `schedule_entries_ibfk_1` FOREIGN KEY (`topic_id`) REFERENCES `topics` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_entries`
--

LOCK TABLES `schedule_entries` WRITE;
/*!40000 ALTER TABLE `schedule_entries` DISABLE KEYS */;
INSERT INTO `schedule_entries` VALUES (39,3,'2026-07-16',2.25,'no'),(40,2,'2026-07-16',1.75,'yes'),(155,5,'2026-07-17',1.50,'no'),(156,2,'2026-07-17',1.25,'no'),(157,3,'2026-07-17',1.25,'no'),(158,5,'2026-07-18',1.25,'no'),(159,2,'2026-07-18',1.00,'no'),(160,3,'2026-07-18',1.00,'no'),(161,4,'2026-07-18',0.75,'no'),(162,5,'2026-07-19',1.25,'no'),(163,2,'2026-07-19',0.75,'no'),(164,3,'2026-07-19',0.75,'no'),(165,4,'2026-07-19',0.75,'no'),(166,6,'2026-07-19',0.50,'no'),(167,5,'2026-07-20',1.25,'no'),(168,2,'2026-07-20',0.75,'no'),(169,3,'2026-07-20',0.75,'no'),(170,4,'2026-07-20',0.75,'no'),(171,6,'2026-07-20',0.50,'no'),(172,5,'2026-07-21',1.25,'no'),(173,2,'2026-07-21',0.75,'no'),(174,3,'2026-07-21',0.75,'no'),(175,4,'2026-07-21',0.75,'no'),(176,6,'2026-07-21',0.50,'no'),(177,2,'2026-07-22',1.25,'no'),(178,3,'2026-07-22',1.00,'no'),(179,4,'2026-07-22',1.00,'no'),(180,6,'2026-07-22',0.75,'no'),(181,2,'2026-07-23',1.25,'no'),(182,3,'2026-07-23',1.00,'no'),(183,4,'2026-07-23',1.00,'no'),(184,6,'2026-07-23',0.75,'no'),(185,4,'2026-07-24',2.50,'no'),(186,6,'2026-07-24',1.50,'no'),(187,4,'2026-07-25',2.50,'no'),(188,6,'2026-07-25',1.50,'no'),(189,4,'2026-07-26',2.50,'no'),(190,6,'2026-07-26',1.50,'no'),(191,6,'2026-07-27',4.00,'no'),(192,6,'2026-07-28',4.00,'no');
/*!40000 ALTER TABLE `schedule_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `test_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `test_id` (`test_id`),
  CONSTRAINT `subjects_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES (1,1,'Algebra','active','2026-07-09 14:42:58','2026-07-09 14:42:58'),(2,1,'Trignomentry','active','2026-07-09 14:43:25','2026-07-09 14:43:25'),(3,2,'Literature','active','2026-07-09 16:08:51','2026-07-09 16:08:51');
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tests`
--

DROP TABLE IF EXISTS `tests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tests` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `exam_date` date NOT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tests`
--

LOCK TABLES `tests` WRITE;
/*!40000 ALTER TABLE `tests` DISABLE KEYS */;
INSERT INTO `tests` VALUES (1,'Math Exam','2026-07-01','active','2026-07-09 14:42:23','2026-07-09 14:42:23'),(2,'SAT Exam','2026-07-08','active','2026-07-09 15:11:44','2026-07-09 15:11:44');
/*!40000 ALTER TABLE `tests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topics`
--

DROP TABLE IF EXISTS `topics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topics` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `subject_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `difficulty_level` tinyint NOT NULL,
  `priority_level` tinyint NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `miss_penalty` int DEFAULT '0',
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `topics_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `topics_chk_1` CHECK ((`difficulty_level` between 1 and 5)),
  CONSTRAINT `topics_chk_2` CHECK ((`priority_level` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topics`
--

LOCK TABLES `topics` WRITE;
/*!40000 ALTER TABLE `topics` DISABLE KEYS */;
INSERT INTO `topics` VALUES (1,1,'Elementary Algebra',3,2,'2025-06-01','2025-06-30',5,'active','2026-07-09 14:46:29'),(2,3,'Complex Number',5,2,'2026-07-10','2026-07-23',4,'active','2026-07-09 16:11:07'),(3,1,'Algebra Basics',3,4,'2026-07-16','2026-07-23',3,'active','2026-07-16 14:35:56'),(4,1,'Geometry Fundamentals',4,3,'2026-07-18','2026-07-26',5,'active','2026-07-16 14:35:56'),(5,2,'Trigonometry',5,5,'2026-07-17','2026-07-21',2,'active','2026-07-16 14:35:56'),(6,3,'Vocabulary',2,2,'2026-07-19','2026-07-28',1,'active','2026-07-16 14:35:56');
/*!40000 ALTER TABLE `topics` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-04 16:26:08
