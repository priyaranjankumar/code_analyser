       IDENTIFICATION DIVISION.
       PROGRAM-ID. B18PGM6.
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
                 INCLUDE DONDCL
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
            MOVE LOW-VALUES TO DONREPOO
            END-IF
            MOVE -1 TO DONIDL.
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
                SEND MAP('DONREPO')
                     MAPSET('B18MPS1')
                     CURSOR
                     ERASE
            END-EXEC.
      *--------- RECEIVE MAP PARA --------------*
       2100-RECEIVE-MAP-PARA.
            EXEC CICS
                RECEIVE MAP('DONREPO')
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
                     MOVE 'CREATE' TO DONMSGO
                      MOVE LOW-VALUES TO DONREPOO
                      MOVE -1 TO DONNAMEL
                      MOVE DFHBMPRO TO DONIDA
                      MOVE 'ENTER DETAILS TO SAVE' TO DONMSGO
                      PERFORM 2000-SEND-MAP-PARA
                      MOVE 1 TO WS-FLAG
                      MOVE 0 TO WS-READ-FLAG
                     WHEN DFHPF2
                      IF ( WS-READ-FLAG NOT = 2 ) THEN
                      MOVE 'PLEASE VIEW FIRST' TO DONMSGO
                      ELSE
                      MOVE 2 TO WS-FLAG
                      MOVE 'VIEW SUCCESSFUL' TO DONMSGO
                      END-IF
                     WHEN DFHPF3
      *-------- GOING BACK TO PGM 3 --------------*
                     EXEC CICS XCTL
                          PROGRAM('B18PGM3')
                     END-EXEC
                     WHEN DFHPF4
                      MOVE LOW-VALUES TO DONREPOO
                      MOVE -1 TO DONIDL
                      MOVE 'ENTER DONORID TO VIEW' TO DONMSGO
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
                       MOVE 'PLEASE CHOOSE ANY OPTION FIRST' TO DONMSGO
                       END-EVALUATE

                     WHEN OTHER
                       MOVE 'INVALID KEY PRESSED' TO DONMSGO
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
             EVALUATE DONIDI
                WHEN LOW-VALUES
                    MOVE -1 TO DONIDL
                    MOVE 'PLEASE ENTER DONORID' TO DONMSGO
                WHEN SPACES
                    MOVE -1 TO DONIDL
                    MOVE 'DONORID CANNOT BE BLANK' TO DONMSGO
                WHEN OTHER
                IF DONIDI IS NUMERIC THEN
                 PERFORM READ-DONOR-PARA
                ELSE
                   MOVE 'INVALID PATIENT ID' TO PMSGO
                END-IF
             END-EVALUATE
            END-EVALUATE.
      *------ READING PATIENT DATA FROM TABLE --*
       READ-DONOR-PARA.
            MOVE DONIDI TO DB-DONOR-ID.
            EXEC SQL
                SELECT
                    DONOR_ID,
                    DONOR_NAME,
                    DONOR_BLOOD_GROUP,
                    DONOR_ADD_ST_NUMBER,
                    DONOR_ADD_ST_NAME1,
                    DONOR_ADD_ST_NAME2,
                    DONOR_ADD_CITY,
                    DONOR_ADD_STATE,
                    DONOR_ADD_COUNTRY,
                    DONOR_ADD_ZIPCD,
                    DONOR_GENDER,
                    DONOR_CONTACT_NUM
                    INTO
                   :DB-DONOR-ID,
                   :DB-DONOR-NAME,
                   :DB-DONOR-BLOOD-GROUP,
                   :DB-DONOR-ADD-ST-NUMBER,
                   :DB-DONOR-ADD-ST-NAME1,
                   :DB-DONOR-ADD-ST-NAME2,
                   :DB-DONOR-ADD-CITY,
                   :DB-DONOR-ADD-STATE,
                   :DB-DONOR-ADD-COUNTRY,
                   :DB-DONOR-ADD-ZIPCD,
                   :DB-DONOR-GENDER,
                   :DB-DONOR-CONTACT-NUM
                   FROM DONOR_DETAIL
                   WHERE DONOR_ID = :DB-DONOR-ID
             END-EXEC.
             EVALUATE SQLCODE
                   WHEN 0
                      MOVE  DB-DONOR-ID TO WS-TEMP
                      MOVE  WS-TEMP(4:) TO DONIDO
                      MOVE  DB-DONOR-NAME TO DONNAMEO
                     STRING DB-DONOR-ADD-ST-NUMBER DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DONOR-ADD-ST-NAME1    DELIMITED BY ' '
                            INTO DONADDO
                     END-STRING
                     STRING DB-DONOR-ADD-ST-NAME2    DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DONOR-ADD-CITY        DELIMITED BY ' '
                            INTO DONADD1O
                     STRING DB-DONOR-ADD-STATE       DELIMITED BY ' '
                            ','                      DELIMITED BY ' '
                            DB-DONOR-ADD-COUNTRY     DELIMITED BY ' '
                            INTO DONADD2O
                     END-STRING
                      MOVE  DB-DONOR-ADD-ZIPCD TO DONZIPO
                      MOVE  DB-DONOR-GENDER      TO DONGENO
                      MOVE  DB-DONOR-CONTACT-NUM TO DONCNUMO
                      MOVE  DB-DONOR-BLOOD-GROUP TO BLDGRPO
                      MOVE 2 TO WS-READ-FLAG
                   WHEN OTHER
                       MOVE LOW-VALUES TO DONREPOO
                       MOVE 'DONOR ID IS INVALIED' TO DONMSGO
                END-EVALUATE.
      *----------- END PROGRAM PARA -----------*
       4000-END-PROGRAM-PARA.
            EXEC CICS
                RETURN
            END-EXEC.

      *-------- HALTING PROGRAM PARA -----------*
       4100-HALT-PROGRAM-PARA.
            EXEC CICS
                RETURN TRANSID('B186')
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
                DDMMYYYY(DONDATEO)
                DATESEP('/')
                ABSTIME(WS-DATE-TIME)
           END-EXEC.
      *------INPUT DATA VALIDATION  ------------*
       INPUT-DATA-VALIDATION.
                  UNSTRING DONADDI DELIMITED BY ',' OR ' '
                  INTO DB-DONOR-ADD-ST-NUMBER, DB-DONOR-ADD-ST-NAME1
                  END-UNSTRING.
                  UNSTRING DONADD1I DELIMITED BY ',' OR ' '
                  INTO DB-DONOR-ADD-ST-NAME2, DB-DONOR-ADD-CITY
                  END-UNSTRING.
                  UNSTRING DONADD2I DELIMITED BY ',' OR ' '
                  INTO DB-DONOR-ADD-STATE, DB-DONOR-ADD-COUNTRY
                  END-UNSTRING.
              EVALUATE TRUE
                WHEN DONNAMEI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONNAMEL
                    MOVE 'PLEASE ENTER NAME' TO DONMSGO
                WHEN NOT (DONNAMEI IS ALPHABETIC)
                    MOVE -1 TO DONNAMEL
                    MOVE 'PLEASE ENTER CORRECT NAME' TO DONMSGO
                WHEN BLDGRPI = SPACES OR LOW-VALUES
                    MOVE   -1 TO BLDGRPL
                    MOVE 'PLEASE ENTER CORRECT BLOODGROUP' TO DONMSGO
                WHEN NOT (BLDGRPI = 'A+' OR 'B+' OR 'AB+' OR 'A-' OR
                'B-' OR 'AB-' OR 'O+' OR 'O-' )
                    MOVE   -1 TO BLDGRPL
                    MOVE 'PLEASE ENTER CORRECT BLOODGROUP' TO DONMSGO
                WHEN DONADDI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADDL
                    MOVE 'PLEASE ENTER ADDRESS' TO DONMSGO
                WHEN DB-DONOR-ADD-ST-NUMBER = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADDL
                    MOVE 'PLEASE ENTER STREET' TO DONMSGO
                WHEN DB-DONOR-ADD-ST-NAME1 = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADDL
                    MOVE 'PLEASE ENTER STREET1' TO DONMSGO
                WHEN DONADD1I = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD1L
                    MOVE 'PLEASE ENTER ADDRESS IN 2ND LINE' TO DONMSGO
                WHEN DB-DONOR-ADD-ST-NAME2 = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD1L
                    MOVE 'PLEASE ENTER STREET2' TO DONMSGO
                WHEN DB-DONOR-ADD-CITY = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD1L
                    MOVE 'PLEASE ENTER CITY' TO DONMSGO
                WHEN DONADD2I = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD2L
                    MOVE 'PLEASE ENTER ADDRESS IN 3RD LINE' TO DONMSGO
                WHEN DB-DONOR-ADD-STATE = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD2L
                    MOVE 'PLEASE ENTER STATE' TO DONMSGO
                WHEN DB-DONOR-ADD-COUNTRY = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONADD2L
                    MOVE 'PLEASE ENTER COUNTRY' TO DONMSGO
                WHEN DONZIPI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONZIPL
                    MOVE 'PLEASE ENTER ZIP CODE' TO DONMSGO
                WHEN NOT ( DONZIPI IS NUMERIC )
                    MOVE   -1 TO DONZIPL
                    MOVE 'PLEASE ENTER CORRECT ZIP CODE' TO DONMSGO
                WHEN NOT (DONGENI = 'MALE' OR DONGENI = 'FEMALE')
                    MOVE   -1 TO DONGENL
                    MOVE 'PLEASE ENTER CORRECT GENDER' TO DONMSGO
                WHEN DONCNUMI = LOW-VALUES OR SPACES
                    MOVE   -1 TO DONCNUML
                    MOVE 'PLEASE ENTER CONTACT NUMBER' TO DONMSGO
                WHEN DONCNUMI IS NOT NUMERIC
                   MOVE   -1 TO DONCNUML
                   MOVE 'PLEASE ENTER CORRECT CONTACT NUMBER' TO DONMSGO
                WHEN OTHER
                  MOVE DONNAMEI TO DB-DONOR-NAME
                  MOVE DONZIPI TO DB-DONOR-ADD-ZIPCD
                  MOVE DONGENI TO DB-DONOR-GENDER
                  MOVE DONCNUMI TO DB-DONOR-CONTACT-NUM
                  MOVE BLDGRPI TO DB-DONOR-BLOOD-GROUP
                  MOVE 1 TO WS-VALID-DATA-FLAG
             END-EVALUATE.
      *--------- WRITING TO TABLE -------------*
       WRITE-TO-DB-PARA.
                  EXEC SQL
                       INSERT INTO DONOR_DETAIL (
                         DONOR_NAME,
                         DONOR_BLOOD_GROUP,
                         DONOR_ADD_ST_NUMBER,
                         DONOR_ADD_ST_NAME1,
                         DONOR_ADD_ST_NAME2,
                         DONOR_ADD_CITY,
                         DONOR_ADD_STATE,
                         DONOR_ADD_COUNTRY,
                         DONOR_ADD_ZIPCD,
                         DONOR_GENDER,
                         DONOR_CONTACT_NUM )
                         VALUES (
                         :DB-DONOR-NAME,
                         :DB-DONOR-BLOOD-GROUP,
                         :DB-DONOR-ADD-ST-NUMBER,
                         :DB-DONOR-ADD-ST-NAME1,
                         :DB-DONOR-ADD-ST-NAME2,
                         :DB-DONOR-ADD-CITY,
                         :DB-DONOR-ADD-STATE,
                         :DB-DONOR-ADD-COUNTRY,
                         :DB-DONOR-ADD-ZIPCD,
                         :DB-DONOR-GENDER,
                         :DB-DONOR-CONTACT-NUM )
                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 'WRITTEN SUCCESSFULLY' TO DONMSGO
                   WHEN OTHER

                       MOVE 'ERROR WHILE WRITING' TO DONMSGO
                 END-EVALUATE
                 EXEC SQL
                      SELECT MAX(DONOR_ID) INTO :DB-DONOR-ID
                       FROM DONOR_DETAIL
                 END-EXEC
                 MOVE DB-DONOR-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO DONIDO.
      *--- UPDATING PATIENT RECORD IN TABLE -----*
       UPDATE-TO-DB-PARA.
                  EXEC SQL
                    UPDATE DONOR_DETAIL SET
                    DONOR_NAME = :DB-DONOR-NAME,
                    DONOR_BLOOD_GROUP = :DB-DONOR-BLOOD-GROUP,
                    DONOR_ADD_ST_NUMBER = :DB-DONOR-ADD-ST-NUMBER,
                    DONOR_ADD_ST_NAME1 = :DB-DONOR-ADD-ST-NAME1,
                    DONOR_ADD_ST_NAME2 = :DB-DONOR-ADD-ST-NAME2,
                    DONOR_ADD_CITY = :DB-DONOR-ADD-CITY,
                    DONOR_ADD_STATE = :DB-DONOR-ADD-STATE,
                    DONOR_ADD_COUNTRY = :DB-DONOR-ADD-COUNTRY,
                    DONOR_ADD_ZIPCD = :DB-DONOR-ADD-ZIPCD,
                    DONOR_GENDER = :DB-DONOR-GENDER,
                    DONOR_CONTACT_NUM = :DB-DONOR-CONTACT-NUM
                    WHERE DONOR_ID = :DB-DONOR-ID

                 END-EXEC
                 EVALUATE SQLCODE
                   WHEN 0
                       MOVE 0 TO WS-READ-FLAG
                       MOVE 0 TO WS-FLAG
                       MOVE 'UPDATE SUCCESSFULLY' TO DONMSGO
                   WHEN OTHER

                       MOVE 'ERROR WHILE UPDATING' TO DONMSGO
                 END-EVALUATE
                 MOVE DB-DONOR-ID TO WS-TEMP.
                 MOVE WS-TEMP(4:) TO DONIDO.
       5000-MAP-FAILED-PARA.
                 MOVE 'SESSION ENDED DUE TO MAPFAIL' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
       5100-ERROR-MSG-PARA.
                 MOVE 'SESSION ENDED DUE TO ERROR' TO WS-END-MSG.
                 PERFORM 4200-PROGRAM-END-MSG.
                 PERFORM 4000-END-PROGRAM-PARA.
