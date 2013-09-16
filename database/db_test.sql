SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `mydb` ;

CREATE SCHEMA IF NOT EXISTS `default_schema` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE IF NOT EXISTS `default_schema`.`cage` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`stimulusevent` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`amplifiers` (
  `type` VARCHAR(20) NULL DEFAULT NULL,
  `serial` INT(11) NOT NULL,
  PRIMARY KEY (`serial`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`file` (
  `type` VARCHAR(3) NOT NULL,
  PRIMARY KEY (`type`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`sex` (
  `name` VARCHAR(14) NOT NULL,
  `symbol` VARCHAR(1) NOT NULL,
  `abbrev` VARCHAR(1) NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE INDEX (`symbol` ASC),
  UNIQUE INDEX (`abbrev` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`led` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`led_stimulation` (
  `id` INT(11) NOT NULL,
  `dateTime` DATETIME NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`results` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`si_prefix` (
  `symbol` VARCHAR(2) NOT NULL,
  `prefix` VARCHAR(5) NOT NULL,
  `E` INT(11) NOT NULL,
  PRIMARY KEY (`symbol`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`protocols` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`recipe` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`experimentvariable` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`people` (
  `id` INT(11) NOT NULL,
  `PrefixName` VARCHAR(50) NULL DEFAULT NULL,
  `FirstName` VARCHAR(50) NULL DEFAULT NULL,
  `MiddleName` VARCHAR(50) NULL DEFAULT NULL,
  `LastName` VARCHAR(50) NULL DEFAULT NULL,
  `Gender` VARCHAR(1) NULL DEFAULT NULL,
  `Birthdate` DATE NULL DEFAULT NULL,
  `Role` VARCHAR(20) NULL DEFAULT NULL,
  `neurotree_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX (`neurotree_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`cagetransefer` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`iacucprotocols` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`citeable` (
  `id` INT(11) NOT NULL,
  `type` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`dob` (
  `id` INT(11) NOT NULL,
  `dateTime` DATETIME NOT NULL,
  `absolute_error` FLOAT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`reagents` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`si_unit` (
  `symbol` VARCHAR(3) NOT NULL,
  `name` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`symbol`, `name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`strain` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`calibrationdata` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`matingrecord` (
  `id` INT(11) NOT NULL,
  `sire_id` INT(11) NULL DEFAULT NULL,
  `dam_id` INT(11) NULL DEFAULT NULL,
  `startDateTime` DATETIME NOT NULL,
  `stopDateTime` DATETIME NULL DEFAULT NULL,
  `dob_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{191906AB-790E-406D-AC28-C39AEBB5752A}` (`dob_id` ASC),
  CONSTRAINT `fk_{191906AB-790E-406D-AC28-C39AEBB5752A}`
    FOREIGN KEY (`dob_id`)
    REFERENCES `default_schema`.`dob` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`project` (
  `id` INT(11) NOT NULL,
  `lab` VARCHAR(15) NOT NULL,
  `iacuc_protocol_id` INT(11) NULL DEFAULT NULL,
  `blurb` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{DED6DC5D-7540-44D8-A528-DFEDBA4B24EF}` (`iacuc_protocol_id` ASC),
  CONSTRAINT `fk_{DED6DC5D-7540-44D8-A528-DFEDBA4B24EF}`
    FOREIGN KEY (`iacuc_protocol_id`)
    REFERENCES `default_schema`.`iacucprotocols` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`stock` (
  `recipe_id` INT(11) NOT NULL,
  `mix_dateTime` DATETIME NOT NULL,
  PRIMARY KEY (`recipe_id`, `mix_dateTime`),
  CONSTRAINT `fk_{F26D0429-00DC-4841-AC50-D0067688811C}`
    FOREIGN KEY (`recipe_id`)
    REFERENCES `default_schema`.`recipe` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`cagerack` (
  `id` INT(11) NOT NULL,
  `row` INT(11) NOT NULL,
  `col` VARCHAR(1) NOT NULL,
  `cage_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`, `row`, `col`),
  INDEX `fk_{B5D137FC-AF40-4AA7-B54C-D3203B77D35C}` (`cage_id` ASC),
  CONSTRAINT `fk_{B5D137FC-AF40-4AA7-B54C-D3203B77D35C}`
    FOREIGN KEY (`cage_id`)
    REFERENCES `default_schema`.`cage` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`datasources` (
  `id` INT(11) NOT NULL,
  `name` VARCHAR(20) NOT NULL,
  `prefix` VARCHAR(2) NOT NULL,
  `unit` VARCHAR(3) NOT NULL,
  `ds_calibration_rec` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{F5F5DF46-21D3-44A1-AA6E-122699C12D48}` (`prefix` ASC),
  INDEX `fk_{7AAC0630-50FA-43B7-BFD0-09F96A51C4B7}` (`unit` ASC),
  INDEX `fk_{F4A0CABB-27D8-4EF6-AD83-986D92B3D75F}` (`ds_calibration_rec` ASC),
  CONSTRAINT `fk_{F5F5DF46-21D3-44A1-AA6E-122699C12D48}`
    FOREIGN KEY (`prefix`)
    REFERENCES `default_schema`.`si_prefix` (`symbol`),
  CONSTRAINT `fk_{7AAC0630-50FA-43B7-BFD0-09F96A51C4B7}`
    FOREIGN KEY (`unit`)
    REFERENCES `default_schema`.`si_unit` (`symbol`),
  CONSTRAINT `fk_{F4A0CABB-27D8-4EF6-AD83-986D92B3D75F}`
    FOREIGN KEY (`ds_calibration_rec`)
    REFERENCES `default_schema`.`calibrationdata` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`users` (
  `id` INT(11) NOT NULL,
  `person_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX (`person_id` ASC),
  CONSTRAINT `fk_{D9B71B53-9ED1-4AEE-ABE3-2DD4D4A384BD}`
    FOREIGN KEY (`person_id`)
    REFERENCES `default_schema`.`people` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`headstage` (
  `id` INT(11) NOT NULL,
  `channel` INT(11) NOT NULL,
  `amp_serial` INT(11) NOT NULL,
  PRIMARY KEY (`id`, `channel`, `amp_serial`),
  INDEX `fk_{B5AF0372-193D-42DA-96CF-A52A789E0E10}` (`amp_serial` ASC),
  CONSTRAINT `fk_{B5AF0372-193D-42DA-96CF-A52A789E0E10}`
    FOREIGN KEY (`amp_serial`)
    REFERENCES `default_schema`.`amplifiers` (`serial`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`litter` (
  `id` INT(11) NOT NULL,
  `sire_id` INT(11) NOT NULL,
  `dam_id` INT(11) NOT NULL,
  `mr_id` INT(11) NULL DEFAULT NULL,
  `dob_id` INT(11) NOT NULL,
  `cage_id` INT(11) NULL DEFAULT NULL,
  `name` VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX (`mr_id` ASC),
  INDEX `fk_{CF53CC25-EEBC-4D12-97E8-D6ADB0782795}` (`dob_id` ASC),
  INDEX `fk_{CA0CAB20-AC53-4BA9-9605-6839F45BCCC0}` (`cage_id` ASC),
  CONSTRAINT `fk_{5478D6F0-10EF-403C-9FF2-3C033111D1B7}`
    FOREIGN KEY (`mr_id`)
    REFERENCES `default_schema`.`matingrecord` (`id`),
  CONSTRAINT `fk_{CF53CC25-EEBC-4D12-97E8-D6ADB0782795}`
    FOREIGN KEY (`dob_id`)
    REFERENCES `default_schema`.`dob` (`id`),
  CONSTRAINT `fk_{CA0CAB20-AC53-4BA9-9605-6839F45BCCC0}`
    FOREIGN KEY (`cage_id`)
    REFERENCES `default_schema`.`cage` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`person_to_project` (
  `person_id` INT(11) NOT NULL,
  `project_id` INT(11) NOT NULL,
  PRIMARY KEY (`person_id`, `project_id`),
  INDEX `fk_{4CA901BE-90FF-4931-B54B-9F456FF3E4B8}` (`project_id` ASC),
  CONSTRAINT `fk_{37244317-C8B0-41B2-B30A-63FB34EA8FFF}`
    FOREIGN KEY (`person_id`)
    REFERENCES `default_schema`.`people` (`id`),
  CONSTRAINT `fk_{4CA901BE-90FF-4931-B54B-9F456FF3E4B8}`
    FOREIGN KEY (`project_id`)
    REFERENCES `default_schema`.`project` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`credentials` (
  `id` INT(11) NOT NULL,
  `user_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{C47EFF3D-6A78-41E8-9232-7E42961C0F1C}` (`user_id` ASC),
  CONSTRAINT `fk_{C47EFF3D-6A78-41E8-9232-7E42961C0F1C}`
    FOREIGN KEY (`user_id`)
    REFERENCES `default_schema`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`solutions` (
  `id` INT(11) NOT NULL,
  `recipe_id` INT(11) NOT NULL,
  `mix_dateTime` DATETIME NULL DEFAULT NULL,
  `stock_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`, `recipe_id`),
  UNIQUE INDEX (`mix_dateTime` ASC),
  INDEX `fk_{3D33DB13-F76E-4C8A-A424-60E4AAF97A4E}` (`recipe_id` ASC),
  INDEX `fk_{16A5408E-CEFC-44AD-B6DE-24E5684F7D3D}` (`stock_id` ASC),
  CONSTRAINT `fk_{3D33DB13-F76E-4C8A-A424-60E4AAF97A4E}`
    FOREIGN KEY (`recipe_id`)
    REFERENCES `default_schema`.`recipe` (`id`),
  CONSTRAINT `fk_{16A5408E-CEFC-44AD-B6DE-24E5684F7D3D}`
    FOREIGN KEY (`stock_id`)
    REFERENCES `default_schema`.`stock` (`mix_dateTime`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`users_datastreams` (
  `datasource_id` INT(11) NOT NULL,
  `users_id` INT(11) NOT NULL,
  PRIMARY KEY (`datasource_id`, `users_id`),
  INDEX `fk_{E2022B44-1C24-436C-A0E3-1535AC52FCB0}` (`users_id` ASC),
  CONSTRAINT `fk_{CBFE2F54-6B6C-4B72-B56A-C97847121EED}`
    FOREIGN KEY (`datasource_id`)
    REFERENCES `default_schema`.`datasources` (`id`),
  CONSTRAINT `fk_{E2022B44-1C24-436C-A0E3-1535AC52FCB0}`
    FOREIGN KEY (`users_id`)
    REFERENCES `default_schema`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`mouse` (
  `id` INT(11) NOT NULL,
  `eartag` INT(11) NULL DEFAULT NULL,
  `tattoo` INT(11) NULL DEFAULT NULL,
  `num_in_lit` INT(11) NULL DEFAULT NULL,
  `name` VARCHAR(20) NULL DEFAULT NULL,
  `cage_id` INT(11) NULL DEFAULT NULL,
  `sex_id` VARCHAR(1) NOT NULL,
  `genotype_id` INT(11) NULL DEFAULT NULL,
  `strain_id` VARCHAR(20) NULL DEFAULT NULL,
  `litter_id` INT(11) NULL DEFAULT NULL,
  `sire_id` INT(11) NULL DEFAULT NULL,
  `dam_id` INT(11) NULL DEFAULT NULL,
  `dob_id` INT(11) NOT NULL,
  `dod` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{E341591B-0406-4162-852A-8D9FF4296E0D}` (`cage_id` ASC),
  INDEX `fk_{396753A1-FE71-40CF-AA4E-DFC6A9FB8792}` (`sex_id` ASC),
  INDEX `fk_{35A4059C-0AC3-4BE4-AEC2-E4F705677D9F}` (`strain_id` ASC),
  INDEX `fk_{11EC2DAB-264C-44D3-869A-695A4F3A2B0F}` (`litter_id` ASC),
  INDEX `fk_{A7F38E92-25DB-4B16-AAA0-368C688E6B85}` (`dob_id` ASC),
  CONSTRAINT `fk_{E341591B-0406-4162-852A-8D9FF4296E0D}`
    FOREIGN KEY (`cage_id`)
    REFERENCES `default_schema`.`cage` (`id`),
  CONSTRAINT `fk_{396753A1-FE71-40CF-AA4E-DFC6A9FB8792}`
    FOREIGN KEY (`sex_id`)
    REFERENCES `default_schema`.`sex` (`abbrev`),
  CONSTRAINT `fk_{35A4059C-0AC3-4BE4-AEC2-E4F705677D9F}`
    FOREIGN KEY (`strain_id`)
    REFERENCES `default_schema`.`strain` (`id`),
  CONSTRAINT `fk_{11EC2DAB-264C-44D3-869A-695A4F3A2B0F}`
    FOREIGN KEY (`litter_id`)
    REFERENCES `default_schema`.`litter` (`id`),
  CONSTRAINT `fk_{A7F38E92-25DB-4B16-AAA0-368C688E6B85}`
    FOREIGN KEY (`dob_id`)
    REFERENCES `default_schema`.`dob` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`repository` (
  `url` VARCHAR(100) NOT NULL,
  `credentials_id` INT(11) NULL DEFAULT NULL,
  `blurb` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`url`),
  INDEX `fk_{60A64E43-ECFC-4C14-9510-5193B92DE468}` (`credentials_id` ASC),
  CONSTRAINT `fk_{60A64E43-ECFC-4C14-9510-5193B92DE468}`
    FOREIGN KEY (`credentials_id`)
    REFERENCES `default_schema`.`credentials` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`experiments` (
  `id` INT(11) NOT NULL,
  `project_id` INT(11) NOT NULL,
  `person_id` INT(11) NOT NULL,
  `mouse_id` INT(11) NOT NULL,
  `startDateTime` DATETIME NOT NULL,
  `protocol_id` INT(11) NULL DEFAULT NULL,
  `exp_type` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{9D8A18F7-52B5-468F-AE6F-BFBF8CE95CC5}` (`project_id` ASC),
  INDEX `fk_{AFEAEB42-7CA6-4072-AFD9-19671CC426F9}` (`person_id` ASC),
  INDEX `fk_{7C88B89C-5FDB-4288-84BE-45DB4D96D57D}` (`mouse_id` ASC),
  INDEX `fk_{F7CA5039-658B-4F8B-BEFC-FC362BFC7F91}` (`protocol_id` ASC),
  CONSTRAINT `fk_{9D8A18F7-52B5-468F-AE6F-BFBF8CE95CC5}`
    FOREIGN KEY (`project_id`)
    REFERENCES `default_schema`.`project` (`id`),
  CONSTRAINT `fk_{AFEAEB42-7CA6-4072-AFD9-19671CC426F9}`
    FOREIGN KEY (`person_id`)
    REFERENCES `default_schema`.`people` (`id`),
  CONSTRAINT `fk_{7C88B89C-5FDB-4288-84BE-45DB4D96D57D}`
    FOREIGN KEY (`mouse_id`)
    REFERENCES `default_schema`.`mouse` (`id`),
  CONSTRAINT `fk_{F7CA5039-658B-4F8B-BEFC-FC362BFC7F91}`
    FOREIGN KEY (`protocol_id`)
    REFERENCES `default_schema`.`protocols` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`breeder` (
  `id` INT(11) NOT NULL,
  `sex` VARCHAR(1) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{9EA7ECE4-2588-493C-9E50-F0837DD916D9}` (`sex` ASC),
  CONSTRAINT `fk_{A71250B2-9631-4094-937F-5D9A9A1AF572}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`mouse` (`id`),
  CONSTRAINT `fk_{9EA7ECE4-2588-493C-9E50-F0837DD916D9}`
    FOREIGN KEY (`sex`)
    REFERENCES `default_schema`.`sex` (`abbrev`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`sliceprep` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{29F06C8D-5D9B-4AB4-89C3-19C161B5B7A2}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`mouse` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`slice` (
  `mouse_id` INT(11) NOT NULL,
  `startDateTime` DATETIME NOT NULL,
  PRIMARY KEY (`mouse_id`, `startDateTime`),
  CONSTRAINT `fk_{8DC2B8F1-1CAA-4DAD-AFF2-B66AD92B3EEE}`
    FOREIGN KEY (`mouse_id`)
    REFERENCES `default_schema`.`mouse` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`repopaths` (
  `id` INT(11) NOT NULL,
  `repo_url` VARCHAR(255) NULL DEFAULT NULL,
  `path` VARCHAR(255) NULL DEFAULT NULL,
  `assoc_program` VARCHAR(15) NULL DEFAULT NULL,
  `blurb` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{4EE1D99D-661F-446F-AC92-74B9A3771A26}` (`repo_url` ASC),
  CONSTRAINT `fk_{4EE1D99D-661F-446F-AC92-74B9A3771A26}`
    FOREIGN KEY (`repo_url`)
    REFERENCES `default_schema`.`repository` (`url`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`sliceexperiment` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{CD97A4CA-E4DB-4BBE-B63F-EF3ABC24AB97}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`experiments` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`cell` (
  `id` INT(11) NOT NULL,
  `mouse_id` INT(11) NOT NULL,
  `slice_sdt` INT(11) NOT NULL,
  `hs_id` INT(11) NOT NULL,
  `experiment_id` INT(11) NOT NULL,
  `startDateTime` DATETIME NOT NULL,
  `esp_x` FLOAT(11) NULL DEFAULT NULL,
  `esp_y` FLOAT(11) NULL DEFAULT NULL,
  `pos_z_rel` FLOAT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{47D72107-1377-48E8-A019-CC9380960495}` (`mouse_id` ASC),
  INDEX `fk_{CBD3D248-22F3-4925-A8B2-45868B723D60}` (`slice_sdt` ASC),
  INDEX `fk_{FFE0ECC1-1D00-410D-B8E3-ED7051651C04}` (`hs_id` ASC),
  INDEX `fk_{9B782A25-A808-4902-8994-A1EB94F23880}` (`experiment_id` ASC),
  CONSTRAINT `fk_{47D72107-1377-48E8-A019-CC9380960495}`
    FOREIGN KEY (`mouse_id`)
    REFERENCES `default_schema`.`mouse` (`id`),
  CONSTRAINT `fk_{CBD3D248-22F3-4925-A8B2-45868B723D60}`
    FOREIGN KEY (`slice_sdt`)
    REFERENCES `default_schema`.`slice` (`startDateTime`),
  CONSTRAINT `fk_{FFE0ECC1-1D00-410D-B8E3-ED7051651C04}`
    FOREIGN KEY (`hs_id`)
    REFERENCES `default_schema`.`headstage` (`id`),
  CONSTRAINT `fk_{9B782A25-A808-4902-8994-A1EB94F23880}`
    FOREIGN KEY (`experiment_id`)
    REFERENCES `default_schema`.`experiments` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`datafile` (
  `repopath_id` INT(11) NOT NULL,
  `filename` VARCHAR(255) NOT NULL,
  `experiment_id` INT(11) NOT NULL,
  `datasource_id` INT(11) NOT NULL,
  `creation_DateTime` DATETIME NOT NULL,
  PRIMARY KEY (`repopath_id`, `filename`),
  INDEX `fk_{62692FF8-6083-4EE4-B60C-C9C8E0A1EDDB}` (`experiment_id` ASC),
  INDEX `fk_{73D3F0F3-DEEB-476C-AE94-F2E82AA90DC7}` (`datasource_id` ASC),
  CONSTRAINT `fk_{08BC833E-B561-41E8-A1D7-D6CEE0C1159C}`
    FOREIGN KEY (`repopath_id`)
    REFERENCES `default_schema`.`repopaths` (`id`),
  CONSTRAINT `fk_{62692FF8-6083-4EE4-B60C-C9C8E0A1EDDB}`
    FOREIGN KEY (`experiment_id`)
    REFERENCES `default_schema`.`experiments` (`id`),
  CONSTRAINT `fk_{73D3F0F3-DEEB-476C-AE94-F2E82AA90DC7}`
    FOREIGN KEY (`datasource_id`)
    REFERENCES `default_schema`.`datasources` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`sire` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{5C8DE539-630B-4A7C-9D5D-51EEF47C0A2E}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`breeder` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`metadata` (
  `experiment_id` INT(11) NOT NULL,
  `datasource_id` INT(11) NOT NULL,
  `dateTime` DATETIME NOT NULL,
  `value` FLOAT(11) NOT NULL,
  `sigfigs` INT(11) NULL DEFAULT NULL,
  `abs_error` FLOAT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`experiment_id`),
  INDEX `fk_{2EA11E4A-B50C-427C-BD84-2B548919BF62}` (`datasource_id` ASC),
  CONSTRAINT `fk_{3C933825-B186-4D9D-83DE-4E6B7712A905}`
    FOREIGN KEY (`experiment_id`)
    REFERENCES `default_schema`.`experiments` (`id`),
  CONSTRAINT `fk_{2EA11E4A-B50C-427C-BD84-2B548919BF62}`
    FOREIGN KEY (`datasource_id`)
    REFERENCES `default_schema`.`datasources` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`waterrecords` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{41B0EF8B-4068-417E-AADF-C12F753227D8}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`experiments` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`dam` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{E975C151-BC99-48CE-94F9-9572E2B43ECF}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`breeder` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`histologyexperiment` (
  `id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_{BFBD58D6-02A1-4704-8BE5-9263F70E9FAA}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`experiments` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`pharmacologydata` (
  `experiment_id` INT(11) NOT NULL,
  `datasource_id` INT(11) NOT NULL,
  `drug_id` INT(11) NOT NULL,
  `solution_id` INT(11) NOT NULL,
  PRIMARY KEY (`experiment_id`, `drug_id`),
  INDEX `fk_{96FA8EB1-8AE1-4615-92B0-E12C3CC548BC}` (`datasource_id` ASC),
  INDEX `fk_{8CD086B9-016C-44B5-8139-7B1B445D1954}` (`drug_id` ASC),
  INDEX `fk_{AD70D770-9C0E-4577-8BF0-0006933FB0F0}` (`solution_id` ASC),
  CONSTRAINT `fk_{A86A14FA-BB72-45F0-8647-1B6652B40379}`
    FOREIGN KEY (`experiment_id`)
    REFERENCES `default_schema`.`experiments` (`id`),
  CONSTRAINT `fk_{96FA8EB1-8AE1-4615-92B0-E12C3CC548BC}`
    FOREIGN KEY (`datasource_id`)
    REFERENCES `default_schema`.`datasources` (`id`),
  CONSTRAINT `fk_{8CD086B9-016C-44B5-8139-7B1B445D1954}`
    FOREIGN KEY (`drug_id`)
    REFERENCES `default_schema`.`reagents` (`id`),
  CONSTRAINT `fk_{AD70D770-9C0E-4577-8BF0-0006933FB0F0}`
    FOREIGN KEY (`solution_id`)
    REFERENCES `default_schema`.`solutions` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`iuepexperiment` (
  `id` INT(11) NOT NULL,
  `matingrecord_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_{800A03A0-BFA9-485C-A5E4-CE32E3E19FB4}` (`matingrecord_id` ASC),
  CONSTRAINT `fk_{AF317A17-1DCE-4AD4-84B3-DDE311695EF6}`
    FOREIGN KEY (`id`)
    REFERENCES `default_schema`.`experiments` (`id`),
  CONSTRAINT `fk_{800A03A0-BFA9-485C-A5E4-CE32E3E19FB4}`
    FOREIGN KEY (`matingrecord_id`)
    REFERENCES `default_schema`.`matingrecord` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `default_schema`.`cell_to_cell` (
  `cell_1_id` INT(11) NOT NULL,
  `cell_2_id` INT(11) NOT NULL,
  PRIMARY KEY (`cell_1_id`, `cell_2_id`),
  INDEX `fk_{87FCB4B8-F88C-4713-9B48-4D23F29915BC}` (`cell_2_id` ASC),
  CONSTRAINT `fk_{4766CF26-3C9D-4484-BF42-15684B8BF486}`
    FOREIGN KEY (`cell_1_id`)
    REFERENCES `default_schema`.`cell` (`id`),
  CONSTRAINT `fk_{87FCB4B8-F88C-4713-9B48-4D23F29915BC}`
    FOREIGN KEY (`cell_2_id`)
    REFERENCES `default_schema`.`cell` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
