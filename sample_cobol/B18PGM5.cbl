       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM5.
      *******************************************
      *        AUTHOR : PRIYA RANJAN KUMAR      *
      *        PROGRAM: DOCTOR RESPOSITORY      *
      *        VERSION: 1.0                     *
      *        DATE   : 28-JUN-2021             *
      *        DESC   : PROGRAM TO INSERT,VIEW  *
      *                UPDATE DOCTOR RECORDS    *
      *******************************************
       DATA DIVISION.
      * --------------------------------------- *
       WORKING-STORAGE SECTION.
      *------- INCLUDING SQL HOST VARIABLES ----*
            EXEC SQL
                 INCLUDE DOCDCL
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
            MOVE LOW-VALUES TO DOCREPOO
            END-IF
            MOVE -1 TO DOCIDL.
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
                SEND MAP('DOCREPO')
                     MAPSET('B18MPS1')
                     CURSOR
                     ERASE
            END-EXEC.
      *--------- RECEIVE MAP PARA --------------*
       2100-RECEIVE-MAP-PARA.
            EXEC CICS
                RECEIVE MAP('DOCREPO')
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
                     MOVE 'CREATE' TO DOCMSGO
                      MOVE LOW-VALUES TO DOCREPOO
                      MOVE -1 TO DOCNAMEL
                      MOVE DFHBMPRO TO DOCIDA
                      MOVE 'ENTER DETAILS TO SAVE' TO DOCMSGO
                      PERFORM 2000-SEND-MAP-PARA
                      MOVE 1 TO WS-FLAG
                      MOVE 0 TO WS-READ-FLAG
                     WHEN DFHPF2
                      IF ( WS-READ-FLAG NOT = 2 ) THEN
                      MOVE 'PLEASE VIEW FIRST' TO DOCMSGO
                      ELSE
                      MOVE 2 TO WS-FLAG
                      MOVE 'VIEW SUCCESSFUL' TO DOCMSGO
                      END-IF
                     WHEN DFHPF3
      *-------- GOING BACK TO PGM 3 --------------*
                     EXEC CICS XCTL
                          PROGRAM('B18PGM3')
                     END-EXEC
                     WHEN DFHPF4
                      MOVE LOW-VALUES TO DOCREPOO
                      MOVE -1 TO DOCIDL
                      MOVE 'ENTER DOCTORID TO VIEW' TO DOCMSGO
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
                       MOVE 'PLEASE CHOOSE ANY OPTION FIRST' TO DOCMSGO
                       END-EVALUATE

                     WHEN OTHER
                       MOVE 'INVALID KEY PRESSED' TO DOCMSGO
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
             EVALUATE DOCIDI
                WHEN LOW-VALUES
                    MOVE -1 TO DOCIDL
                    MOVE 'PLEASE ENTER DOCTORID' TO DOCMSGO
                WHEN SPACES
                    MOVE -1 TO DOCIDL
                    MOVE 'DOCTORID CANNOT BE BLANK' TO DOCMSGO
                WHEN OTHER
                IF DOCIDI IS NUMERIC THEN
                 PERFORM READ-DOCTOR-PARA
                ELSE
                   MOVE 'INVALID PATIENT ID' TO PMSGO
                END-IF
             END-EVALUATE
            END-EVALUATE.
      *------ READING PATIENT DATA FROM TABLE --*
       READ-DOCTOR-PARA.
            MOVE DOCIDI TO DB-DOCTOR-ID.
            EXEC SQL
                SELECT
                    DOCTOR_ID,
                    DOCTOR_NAME,
                    DOCTOR_ADD_ST_NUMBER,
                    DOCTOR_ADD_ST_NAME1,
                    DOCTOR_ADD_ST_NAME2,
                    DOCTOR_ADD_CITY,
                    DOCTOR_ADD_STATE,
                    DOCTOR_ADD_COUNTRY,
                    DOCTOR_ADD_ZIPCD,
                    DOCTOR_GENDER,
                    DOCTOR_CONTACT_NUM
                    INTO
                   :DB-DOCTOR-ID,
                   :DB-DOCTOR-NAME,
                   :DB-DOCTOR-ADD-ST-NUMBER,
                   :DB-DOCTOR-ADD-ST-NAME1,
                   :DB-DOCTOR-ADD-ST-NAME2,
                   :DB-DOCTOR-ADD-CITY,
                   :DB-DOCTOR-ADD-STATE,
                   :DB-DOCTOR-ADD-COUNTRY,
                   :DB-DOCTOR-ADD-ZIPCD,
                   :DB-DOCTOR-GENDER,
                   :DB-DOCTOR-CONTACT-NUM
                   FROM DOCTOR_DETAIL
                   WHERE DOCTOR_ID = :DB-DOCTOR-ID
             END-EXEC.
             EVALUATE SQLCODE
                   WHEN 0
                      MOVE  DB-DOCTOR-ID TO WS-TEMP
                      MOVE  WS-TEMP(4:) TO DOCIDO
                      MOVE  DB-DOCTOR-NAME TO DOCNAMEO
                     STRING DB-DOCTOR-ADD-ST-NUMBER DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DOCTOR-ADD-ST-NAME1   DELIMITED BY ' '
                            INTO DOCADDO
                     END-STRING
                     STRING DB-DOCTOR-ADD-ST-NAME2   DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DOCTOR-ADD-CITY       DELIMITED BY ' '
                            INTO DOCADD1O
                     STRING DB-DOCTOR-ADD-STATE      DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DOCTOR-ADD-COUNTRY    DELIMITED BY ' '
                            INTO DOCADD2O
                     END-STRING
                      MOVE  DB-DOCTOR-ADD-ZIPCD TO DOCZIPO
                      MOVE  DB-DOCTOR-GENDER     TO DOCGENO
                      MOVE  DB-DOCTOR-CONTACT-NUM TO DOCCNUMO
                      MOVE 2 TO WS-READ-FLAG
                   WHEN OTHER
                       MOVE LOW-VALUES TO DOCREPOO
                       MOVE 'DOCTOR ID IS INVALIED' TO DOCMSGO
                END-EVALUATE.
      *----------- END PROGRAM PARA -----------*
       4000-END-PROGRAM-PARA.
            EXEC CICS
                RETURN
            END-EXEC.

      *-------- HALTING PROGRAM PARA -----------*
       4100-HALT-PROGRAM-PARA.
            EXEC CICS
                RETURN TRANSID('B185')
                COMMAREA(WS-COMMAREA)
            END-EXEC.
      *-------- SENDING END MESSAGE PARA -------*
       4200-PROGRAM-END-MSG.
           EXEC CICS
                SEND FROM(WS-END-MSG)
                     LENGTH(WS-END-MSG-LEN)
                     ERASE
           END-EXEC.
      *----- GETTING DATE FROM SYSTEM ----------*
       GET-DATE-TIME-PARA.
           EXEC CICS
                ASKTIME
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
           EXEC CICS
                FORMATTIME
                DDMMYYYY(DOCDATEO)
                DATESEP('/')
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
      *------INPUT DATA VALIDATION  ------------*
       INPUT-DATA-VALIDATION.
                  UNSTRING DOCADDI DELIMITED BY ',' OR ' '
                  INTO DB-DOCTOR-ADD-ST-NUMBER, DB-DOCTOR-ADD-ST-NAME1
                  END-UNSTRING.
                  UNSTRING DOCADD1I DELIMITED BY ',' OR ' '
                  INTO DB-DOCTOR-ADD-ST-NAME2, DB-DOCTOR-ADD-CITY
                  END-UNSTRING.
                  UNSTRING DOCADD2I DELIMITED BY ',' OR ' '
                  INTO DB-DOCTOR-ADD-STATE, DB-DOCTOR-ADD-COUNTRY
                  END-UNSTRING.
              EVALUATE TRUE
                WHEN DOCNAMEI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCNAMEL
                    MOVE 'PLEASE ENTER NAME' TO DOCMSGO
                WHEN NOT (DOCNAMEI IS ALPHABETIC)
                    MOVE -1 TO DONNAMEL
                    MOVE 'PLEASE ENTER CORRECT NAME' TO DOCMSGO
                WHEN DOCNAMEI IS NOT ALPHABETIC
                    MOVE   -1 TO DOCNAMEL
                    MOVE 'PLEASE ENTER CORRECT NAME' TO DOCMSGO
                WHEN DOCADDI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADDL
                    MOVE 'PLEASE ENTER ADDRESS' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-ST-NUMBER = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADDL
                    MOVE 'PLEASE ENTER STREET' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-ST-NAME1 = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADDL
                    MOVE 'PLEASE ENTER STREET1' TO DOCMSGO
                WHEN DOCADD1I = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD1L
                    MOVE 'PLEASE ENTER ADDRESS IN 2ND LINE' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-ST-NAME2 = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD1L
                    MOVE 'PLEASE ENTER STREET2' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-CITY = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD1L
                    MOVE 'PLEASE ENTER CITY' TO DOCMSGO
                WHEN DOCADD2I = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD2L
                    MOVE 'PLEASE ENTER ADDRESS IN 3RD LINE' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-STATE = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD2L
                    MOVE 'PLEASE ENTER STATE' TO DOCMSGO
                WHEN DB-DOCTOR-ADD-COUNTRY = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCADD2L
                    MOVE 'PLEASE ENTER COUNTRY' TO DOCMSGO
                WHEN DOCZIPI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCZIPL
                    MOVE 'PLEASE ENTER ZIP CODE' TO DOCMSGO
                WHEN NOT (DOCZIPI IS NUMERIC )
                    MOVE   -1 TO DOCZIPL
                    MOVE 'PLEASE ENTER CORRECT ZIP CODE' TO DOCMSGO
                WHEN NOT (DOCGENI = 'MALE' OR DOCGENI = 'FEMALE')
                    MOVE   -1 TO DOCGENL
                    MOVE 'PLEASE ENTER CORRECT GENDER' TO DOCMSGO
                WHEN DOCCNUMI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DOCCNUML
                    MOVE 'PLEASE ENTER CONTACT NUMBER' TO DOCMSGO
                WHEN DOCCNUMI IS NOT NUMERIC
                   MOVE   -1 TO DOCCNUML
                   MOVE 'PLEASE ENTER CORRECT CONTACT NUMBER' TO DOCMSGO
                WHEN OTHER
                  MOVE DOCNAMEI TO DB-DOCTOR-NAME
                  MOVE DOCZIPI TO DB-DOCTOR-ADD-ZIPCD
                  MOVE DOCGENI TO DB-DOCTOR-GENDER
                  MOVE DOCCNUMI TO DB-DOCTOR-CONTACT-NUM
                  MOVE 1 TO WS-VALID-DATA-FLAG
             END-EVALUATE.
      *--------- WRITING TO TABLE -------------*
       WRITE-TO-DB-PARA.
                  EXEC SQL
                       INSERT INTO DOCTOR_DETAIL (
                         DOCTOR_NAME,
                         DOCTOR_ADD_ST_NUMBER,
                         DOCTOR_ADD_ST_NAME1,
                         DOCTOR_ADD_ST_NAME2,
                         DOCTOR_ADD_CITY,
                         DOCTOR_ADD_STATE,
                         DOCTOR_ADD_COUNTRY,
                         DOCTOR_ADD_ZIPCD,
                         DOCTOR_GENDER,
                         DOCTOR_CONTACT_NUM )
                         VALUES (
                         :DB-DOCTOR-NAME,
                         :DB-DOCTOR-ADD-ST-NUMBER,
                         :DB-DOCTOR-ADD-ST-NAME1,
                         :DB-DOCTOR-ADD-ST-NAME2,
                         :DB-DOCTOR-ADD-CITY,
                         :DB-DOCTOR-ADD-STATE,
                         :DB-DOCTOR-ADD-COUNTRY,
                         :DB-DOCTOR-ADD-ZIPCD,
                         :DB-DOCTOR-GENDER,
                         :DB-DOCTOR-CONTACT-NUM )
                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 'WRITTEN SUCCESSFULLY' TO DOCMSGO
                   WHEN OTHER

                       MOVE 'ERROR WHILE WRITING' TO DOCMSGO
                 END-EVALUATE
                 EXEC SQL
                      SELECT MAX(DOCTOR_ID) INTO :DB-DOCTOR-ID
                       FROM DOCTOR_DETAIL
                 END-EXEC
                 MOVE DB-DOCTOR-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO DOCIDO.
      *--- UPDATING PATIENT RECORD IN TABLE -----*
       UPDATE-TO-DB-PARA.
                  EXEC SQL
                    UPDATE DOCTOR_DETAIL SET
                    DOCTOR_NAME = :DB-DOCTOR-NAME,
                    DOCTOR_ADD_ST_NUMBER = :DB-DOCTOR-ADD-ST-NUMBER,
                    DOCTOR_ADD_ST_NAME1 = :DB-DOCTOR-ADD-ST-NAME1,
                    DOCTOR_ADD_ST_NAME2 = :DB-DOCTOR-ADD-ST-NAME2,
                    DOCTOR_ADD_CITY = :DB-DOCTOR-ADD-CITY,
                    DOCTOR_ADD_STATE = :DB-DOCTOR-ADD-STATE,
                    DOCTOR_ADD_COUNTRY = :DB-DOCTOR-ADD-COUNTRY,
                    DOCTOR_ADD_ZIPCD = :DB-DOCTOR-ADD-ZIPCD,
                    DOCTOR_GENDER = :DB-DOCTOR-GENDER,
                    DOCTOR_CONTACT_NUM = :DB-DOCTOR-CONTACT-NUM
                    WHERE DOCTOR_ID = :DB-DOCTOR-ID

                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 0 TO WS-READ-FLAG
                       MOVE 0 TO WS-FLAG
                       MOVE 'UPDATE SUCCESSFULLY' TO DOCMSGO
                   WHEN OTHER

                       MOVE 'ERROR WHILE UPDATING' TO DOCMSGO
                 END-EVALUATE
                 MOVE DB-DOCTOR-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO DOCIDO.

       5000-MAP-FAILED-PARA.
                 MOVE 'SESSION ENDED DUE TO MAPFAIL' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
       5100-ERROR-MSG-PARA.
                 MOVE 'SESSION ENDED DUE TO ERROR' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
