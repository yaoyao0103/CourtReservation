# NTHU_alb_reserve

In the setting file, you need to fill the information as below.

```json
{
  "id": "112XXXXXX",
  "password": "yourpassword",
  "field1": "3",
  "time1": "12",
  "field2": "3",
  "time2": "13"
}
```

### Notice

- The "field" means the number you need.
- The "time" means the period you need. Be careful, it should be an integer between `""`. For exxample, `7:00~8:00` is `"1"`, `8:00~9:00` is `"2"`, and so on.
- The program cannot be closed until 12:00AM. It has to be executed in the backgroud.

### Usage

##### Go to the project root folder and run the below command to install all required packages.

```
pip install -r requirements.txt
```

##### After that, go into ./src folder and run main.py with arguments.

```
python main.py --id {your_id} --password {your_password} --field1 {field 1} --time1 {field 1's time} --field2 {field 2} --time2 {field 2's time} --linetoken {your_line_notity_token}
```

For example,

```
python main.py --id 112123456 --password 123456789 --field1 2 --time1 12 --field2 2 --time2 13 --linetoken sjdbngvklsskjvnskdjvnslkdnv
```
