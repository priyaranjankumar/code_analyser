       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM4.
      *******************************************
      *        AUTHOR : PRIYA RANJAN KUMAR      *
      *        PROGRAM: PATIENT RESPOSITORY     *
      *        VERSION: 1.0                     *
      *        DATE   : 28-JUN-2021             *
      *        DESC   : PROGRAM TO INSERT,VIEW  *
      *                UPDATE PATIENT RECORDS   *
      *******************************************
       DATA DIVISION.
      * --------------------------------------- *
       WORKING-STORAGE SECTION.
      *------- INCLUDING SQL HOST VARIABLES ----*
            EXEC SQL
                 INCLUDE PATDCL
            END-EXEC.

      *--- INCLUDING SQL COMMUNICATION AREA ----*
            EXEC SQL
                 INCLUDE SQLCA
            END-EXEC.

      *--------- COPYBOOK ----------------------*
       COPY B18MPS1.
       COPY DFHAID.
       COPY DFHBMSCA.
       01 WS-COMMAREA.
          05 WS-FLAG         PIC 9(1).
          05 WS-READ-FLAG    PIC 9(1).
       01 WS-DATE-TIME    PIC S9(15) COMP-3.
       01 WS-END-MSG      PIC X(27) VALUE 'PROGRAM ENDED PLEASE CLEAR'.
       01 WS-END-MSG-LEN  PIC S9(4) COMP VALUE 27.
       01 WS-RESP         PIC S9(8) COMP.
       01 WS-TEMP         PIC X(18).
       01 WS-VALID-DATA-FLAG PIC 9(01) VALUE 0.
       LINKAGE SECTION.
       01 DFHCOMMAREA.
          05 LS-FLAG      PIC 9(1).
          05 LS-READ-FLAG PIC 9(1).
       PROCEDURE DIVISION.
       1000-MAIN-PARA.

            MOVE LS-FLAG TO WS-FLAG.
            MOVE LS-READ-FLAG TO WS-READ-FLAG.
            IF ( LS-READ-FLAG NOT = 2 ) THEN
            MOVE LOW-VALUES TO PATREPOO
            END-IF
            MOVE -1 TO PATIDL.
            EVALUATE EIBCALEN
              WHEN 0
                   PERFORM 2000-SEND-MAP-PARA
              WHEN OTHER
                   PERFORM 3000-KEY-VALIDATION-PARA
                   PERFORM 2000-SEND-MAP-PARA
            END-EVALUATE.
            PERFORM 4100-HALT-PROGRAM-PARA.
      *--------- SEND MAP PARA -----------------*
       2000-SEND-MAP-PARA.
            PERFORM GET-DATE-TIME-PARA.
            EXEC CICS
                SEND MAP('PATREPO')
                     MAPSET('B18MPS1')
                     CURSOR
                     ERASE
            END-EXEC.
      *--------- RECEIVE MAP PARA --------------*
       2100-RECEIVE-MAP-PARA.
            EXEC CICS
                RECEIVE MAP('PATREPO')
                        MAPSET('B18MPS1')
                        RESP(WS-RESP)
            END-EXEC.
            EVALUATE WS-RESP
                WHEN DFHRESP(NORMAL)
                    CONTINUE
                WHEN DFHRESP(MAPFAIL)
                    PERFORM 5000-MAP-FAILED-PARA
                WHEN OTHER
                    PERFORM 5100-ERROR-MSG-PARA
            END-EVALUATE.
      *----CHECKING WHICH KEY IS PRESSED -------*
       3000-KEY-VALIDATION-PARA.
            EVALUATE EIBAID
                     WHEN DFHPF1
                     MOVE 'CREATE' TO PMSGO
                      MOVE LOW-VALUES TO PATREPOO
                      MOVE -1 TO PNAMEL
                      MOVE DFHBMPRO TO PATIDA
                      MOVE 'ENTER DETAILS TO SAVE' TO PMSGO
                      PERFORM 2000-SEND-MAP-PARA
                      MOVE 1 TO WS-FLAG
                      MOVE 0 TO WS-READ-FLAG
                     WHEN DFHPF2
                      IF ( WS-READ-FLAG NOT = 2 ) THEN
                      MOVE 'PLEASE VIEW FIRST' TO PMSGO
                      ELSE
                      MOVE 2 TO WS-FLAG
                      MOVE 'VIEW SUCCESSFUL' TO PMSGO
                      END-IF
                     WHEN DFHPF3
      *-------- GOING BACK TO PGM 3 --------------*
                     EXEC CICS XCTL
                          PROGRAM('B18PGM3')
                     END-EXEC
                     WHEN DFHPF4
                      MOVE LOW-VALUES TO PATREPOO
                      MOVE -1 TO PATIDL
                      MOVE 'ENTER PATIENTID TO VIEW' TO PMSGO
                      PERFORM 2000-SEND-MAP-PARA
                      MOVE 4 TO WS-FLAG
                     WHEN DFHENTER
                      EVALUATE WS-FLAG
                       WHEN 1
                       PERFORM 2100-RECEIVE-MAP-PARA
                       PERFORM 3100-DATA-VALIDATION-PARA

                       WHEN 2
                       PERFORM 2100-RECEIVE-MAP-PARA
                       PERFORM 3100-DATA-VALIDATION-PARA
                       WHEN 4
                       PERFORM 2100-RECEIVE-MAP-PARA
                       PERFORM 3100-DATA-VALIDATION-PARA
                       WHEN OTHER
                       MOVE 'PLEASE CHOOSE ANY OPTION FIRST' TO PMSGO
                       END-EVALUATE

                     WHEN OTHER
                       MOVE 'INVALID KEY PRESSED' TO PMSGO
            END-EVALUATE.
      *----VALIDATING DATA ---------------------*
       3100-DATA-VALIDATION-PARA.
            EVALUATE LS-FLAG
             WHEN 1
              PERFORM INPUT-DATA-VALIDATION
              IF(WS-VALID-DATA-FLAG = 1) THEN
              PERFORM WRITE-TO-DB-PARA
              END-IF
             WHEN 2
              PERFORM INPUT-DATA-VALIDATION
              IF(WS-VALID-DATA-FLAG = 1) THEN
              PERFORM UPDATE-TO-DB-PARA
              END-IF
             WHEN 4
             EVALUATE PATIDI
                WHEN LOW-VALUES
                    MOVE -1 TO PATIDL
                    MOVE 'PLEASE ENTER PATIENTID' TO PMSGO
                WHEN SPACES
                    MOVE -1 TO PATIDL
                    MOVE 'PATIENTID CANNOT BE BLANK' TO PMSGO
                WHEN OTHER
                  IF PATIDI IS NUMERIC THEN
                    PERFORM READ-PATIENT-PARA
                  ELSE
                    MOVE 'INVALID PATIENT ID' TO PMSGO
                  END-IF
             END-EVALUATE
            END-EVALUATE.
      *------ READING PATIENT DATA FROM TABLE --*
       READ-PATIENT-PARA.
            MOVE PATIDI TO DB-PATIENT-ID.
            EXEC SQL
                SELECT
                    PATIENT_ID,
                    PATIENT_NAME,
                    PATIENT_ADD_ST_NUMBER,
                    PATIENT_ADD_ST_NAME1,
                    PATIENT_ADD_ST_NAME2,
                    PATIENT_ADD_CITY,
                    PATIENT_ADD_STATE,
                    PATIENT_ADD_COUNTRY,
                    PATIENT_ADD_ZIPCD,
                    PATIENT_DOB,
                    PATIENT_GENDER,
                    PATIENT_CONTACT_NUM
                    INTO
                   :DB-PATIENT-ID,
                   :DB-PATIENT-NAME,
                   :DB-PATIENT-ADD-ST-NUMBER,
                   :DB-PATIENT-ADD-ST-NAME1,
                   :DB-PATIENT-ADD-ST-NAME2,
                   :DB-PATIENT-ADD-CITY,
                   :DB-PATIENT-ADD-STATE,
                   :DB-PATIENT-ADD-COUNTRY,
                   :DB-PATIENT-ADD-ZIPCD,
                   :DB-PATIENT-DOB,
                   :DB-PATIENT-GENDER,
                   :DB-PATIENT-CONTACT-NUM
                   FROM PATIENT_DETAIL
                   WHERE PATIENT_ID = :DB-PATIENT-ID
             END-EXEC.
             EVALUATE SQLCODE
                   WHEN 0
                      MOVE  DB-PATIENT-ID TO WS-TEMP
                      MOVE  WS-TEMP(4:) TO PATIDO
                      MOVE  DB-PATIENT-NAME TO PNAMEO
                     STRING DB-PATIENT-ADD-ST-NUMBER DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-PATIENT-ADD-ST-NAME1  DELIMITED BY ' '
                            INTO PADDO
                     END-STRING
                     STRING DB-PATIENT-ADD-ST-NAME2  DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-PATIENT-ADD-CITY      DELIMITED BY ' '
                            INTO PADD1O
                     STRING DB-PATIENT-ADD-STATE     DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-PATIENT-ADD-COUNTRY   DELIMITED BY ' '
                            INTO PADD2O
                     END-STRING
                      MOVE  DB-PATIENT-ADD-ZIPCD TO PZIPO
                      MOVE  DB-PATIENT-DOB       TO PBDATEO
                      MOVE  DB-PATIENT-GENDER    TO PGENO
                      MOVE  DB-PATIENT-CONTACT-NUM TO PCNUMO
                      MOVE 2 TO WS-READ-FLAG
                   WHEN OTHER
                       MOVE LOW-VALUES TO PATREPOO
                       MOVE -1 TO PATIDL
                       MOVE 'PATIENT ID IS INVALIED' TO PMSGO
                END-EVALUATE.
      *----------- END PROGRAM PARA -----------*
       4000-END-PROGRAM-PARA.
            EXEC CICS
                RETURN
            END-EXEC.

      *-------- HALTING PROGRAM PARA -----------*
       4100-HALT-PROGRAM-PARA.
            EXEC CICS
                RETURN TRANSID('B184')
                COMMAREA(WS-COMMAREA)
            END-EXEC.
      *-------- SENDING END MESSAGE PARA -------*
       4200-PROGRAM-END-MSG.
           EXEC CICS
                SEND FROM(WS-END-MSG)
                     LENGTH(WS-END-MSG-LEN)
                     ERASE
           END-EXEC.
      *----- GETTING DATE FROM SYSTEM     ------*
       GET-DATE-TIME-PARA.
           EXEC CICS
                ASKTIME
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
           EXEC CICS
                FORMATTIME
                DDMMYYYY(PDATEO)
                DATESEP('/')
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
      *------INPUT DATA VALIDATION  ------------*
       INPUT-DATA-VALIDATION.
                  UNSTRING PADDI DELIMITED BY ',' OR ' '
                  INTO DB-PATIENT-ADD-ST-NUMBER, DB-PATIENT-ADD-ST-NAME1
                  END-UNSTRING.
                  UNSTRING PADD1I DELIMITED BY ',' OR ' '
                  INTO DB-PATIENT-ADD-ST-NAME2, DB-PATIENT-ADD-CITY
                  END-UNSTRING.
                  UNSTRING PADD2I DELIMITED BY ',' OR ' '
                  INTO DB-PATIENT-ADD-STATE, DB-PATIENT-ADD-COUNTRY
                  END-UNSTRING.
              EVALUATE TRUE
                WHEN PNAMEI = LOW-VALUES OR SPACES
                    MOVE   -1 TO PNAMEL
                    MOVE 'PLEASE ENTER NAME' TO PMSGO
                WHEN NOT (PNAMEI IS ALPHABETIC)
                    MOVE -1 TO PNAMEL
                    MOVE 'PLEASE ENTER CORRECT NAME' TO PMSGO
                WHEN PADDI  = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADDL
                    MOVE 'PLEASE ENTER ADDRESS' TO PMSGO
                WHEN DB-PATIENT-ADD-ST-NUMBER = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADDL
                    MOVE 'PLEASE ENTER STREET' TO PMSGO
                WHEN DB-PATIENT-ADD-ST-NAME1 = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADDL
                    MOVE 'PLEASE ENTER STREET NAME' TO PMSGO
                WHEN PADD1I = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD1L
                    MOVE 'PLEASE ENTER ADDRESS IN 2ND LINE' TO PMSGO
                WHEN DB-PATIENT-ADD-ST-NAME2 = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD1L
                    MOVE 'PLEASE ENTER STREET2' TO PMSGO
                WHEN DB-PATIENT-ADD-CITY = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD1L
                    MOVE 'PLEASE ENTER CITY' TO PMSGO
                WHEN PADD2I = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD2L
                    MOVE 'PLEASE ENTER ADDRESS IN 3RD LINE' TO PMSGO
                WHEN DB-PATIENT-ADD-STATE = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD2L
                    MOVE 'PLEASE ENTER STATE' TO PMSGO
                WHEN DB-PATIENT-ADD-COUNTRY = LOW-VALUES OR SPACES
                    MOVE   -1 TO PADD2L
                    MOVE 'PLEASE ENTER COUNTRY' TO PMSGO
                WHEN PZIPI  = LOW-VALUES OR SPACES
                    MOVE   -1 TO PZIPL
                    MOVE 'PLEASE ENTER ZIP CODE' TO PMSGO
                WHEN NOT (PZIPI IS NUMERIC)
                    MOVE   -1 TO PZIPL
                    MOVE 'PLEASE ENTER CORRECT ZIP CODE' TO PMSGO
                WHEN NOT (PGENI = 'MALE' OR PGENI = 'FEMALE' )
                    MOVE   -1 TO PGENL
                    MOVE 'PLEASE ENTER CORRECT GENDER' TO PMSGO
                WHEN PCNUMI = LOW-VALUES OR SPACES
                    MOVE   -1 TO PCNUML
                    MOVE 'PLEASE ENTER CONTACT NUMBER' TO PMSGO
                WHEN PCNUMI IS NOT NUMERIC
                    MOVE   -1 TO PCNUML
                    MOVE 'PLEASE ENTER CORRECT CONTACT NUMBER' TO PMSGO
                WHEN PBDATEI = LOW-VALUES OR SPACES
                    MOVE   -1 TO PBDATEL
                    MOVE 'PLEASE ENTER THE BIRHT DATE' TO PMSGO
                WHEN OTHER
                  MOVE PNAMEI TO  DB-PATIENT-NAME
                  MOVE PZIPI  TO  DB-PATIENT-ADD-ZIPCD
                  MOVE PGENI  TO  DB-PATIENT-GENDER
                  MOVE PBDATEI TO DB-PATIENT-DOB
                  MOVE PCNUMI TO  DB-PATIENT-CONTACT-NUM
                  MOVE 1 TO WS-VALID-DATA-FLAG
             END-EVALUATE.
      *--------- WRITING TO TABLE -------------*
       WRITE-TO-DB-PARA.
                  EXEC SQL
                       INSERT INTO PATIENT_DETAIL (
                         PATIENT_NAME,
                         PATIENT_ADD_ST_NUMBER,
                         PATIENT_ADD_ST_NAME1,
                         PATIENT_ADD_ST_NAME2,
                         PATIENT_ADD_CITY,
                         PATIENT_ADD_STATE,
                         PATIENT_ADD_COUNTRY,
                         PATIENT_ADD_ZIPCD,
                         PATIENT_DOB,
                         PATIENT_GENDER,
                         PATIENT_CONTACT_NUM )
                         VALUES (
                         :DB-PATIENT-NAME,
                         :DB-PATIENT-ADD-ST-NUMBER,
                         :DB-PATIENT-ADD-ST-NAME1,
                         :DB-PATIENT-ADD-ST-NAME2,
                         :DB-PATIENT-ADD-CITY,
                         :DB-PATIENT-ADD-STATE,
                         :DB-PATIENT-ADD-COUNTRY,
                         :DB-PATIENT-ADD-ZIPCD,
                         :DB-PATIENT-DOB,
                         :DB-PATIENT-GENDER,
                         :DB-PATIENT-CONTACT-NUM )
                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 'WRITTEN SUCCESSFULLY' TO PMSGO
                   WHEN OTHER

                       MOVE 'ERROR WHILE WRITING' TO PMSGO
                 END-EVALUATE
                 EXEC SQL
                      SELECT MAX(PATIENT_ID) INTO :DB-PATIENT-ID
                       FROM PATIENT_DETAIL
                 END-EXEC
                 MOVE DB-PATIENT-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO PATIDO.
      *--- UPDATING PATIENT RECORD IN TABLE -----*
       UPDATE-TO-DB-PARA.
                  EXEC SQL
                    UPDATE PATIENT_DETAIL SET
                    PATIENT_NAME = :DB-PATIENT-NAME,
                    PATIENT_ADD_ST_NUMBER = :DB-PATIENT-ADD-ST-NUMBER,
                    PATIENT_ADD_ST_NAME1 = :DB-PATIENT-ADD-ST-NAME1,
                    PATIENT_ADD_ST_NAME2 = :DB-PATIENT-ADD-ST-NAME2,
                    PATIENT_ADD_CITY = :DB-PATIENT-ADD-CITY,
                    PATIENT_ADD_STATE = :DB-PATIENT-ADD-STATE,
                    PATIENT_ADD_COUNTRY = :DB-PATIENT-ADD-COUNTRY,
                    PATIENT_ADD_ZIPCD = :DB-PATIENT-ADD-ZIPCD,
                    PATIENT_DOB = :DB-PATIENT-DOB,
                    PATIENT_GENDER = :DB-PATIENT-GENDER,
                    PATIENT_CONTACT_NUM = :DB-PATIENT-CONTACT-NUM
                    WHERE PATIENT_ID = :DB-PATIENT-ID

                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 'UPDATE SUCCESSFULLY' TO PMSGO
                       MOVE 0 TO WS-READ-FLAG
                       MOVE 0 TO WS-FLAG
                   WHEN OTHER

                       MOVE 'ERROR WHILE UPDATING' TO PMSGO
                 END-EVALUATE
                 MOVE DB-PATIENT-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO PATIDO.

       5000-MAP-FAILED-PARA.
                 MOVE 'SESSION ENDED DUE TO MAPFAIL' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
       5100-ERROR-MSG-PARA.
                 MOVE 'SESSION ENDED DUE TO ERROR' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
