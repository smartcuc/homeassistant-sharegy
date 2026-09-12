# Growatt OpenAPI Complete Reference Documentation (ShowDoc)

> **Quelle**: [Growatt OpenAPI ShowDoc (Item 2540838290984246)](https://www.showdoc.com.cn/2540838290984246)

Inhaltsverzeichnis aller OpenAPI-Endpunkte, Datenmodelle und Steuerungsbefehle:

# 1. Document Explanation

*Page ID: `11292912972201443`*

**Fixed Parameters**

token: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (The token is generally defined as a 32-character verification code)

Test token: wa265d2h1og0873ml07142r81564hho6

To obtain token verification, please apply for an OSS account and request it yourself.



**Open Platform Overview**

- Growatt's OpenAPI platform provides standardized RESTful data call services for authenticated users.

- The platform interface is based on the http(s) protocol and uses the OAuth2.0 authentication mechanism.

- API usage process:
  To obtain token verification, please apply for an OSS account and request it yourself:
  https://oss.growatt.com/index (for Europe and other global users),
  https://oss-cn.growatt.com/index (for Chinese users),
  https://oss-us.growatt.com/index (for North American users),
  https://oss-au.growatt.com/login (for Australian and New Zealand users)


![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=1d4413d9b84d94b78ced24e24360012e&amp;file=file.png)




- TOKEN Validity Period
  Approved: Permanent
Copy

---

# 2. Interface Documentation Description

*Page ID: `11292913165257193`*

**Address Header:**
#   Test Address:
http(s)://183.62.216.35:8081/v4

#  Official Address:
 Please use the new domain to access
 (https://server-cn.growatt.com -&gt; https://openapi-cn.growatt.com) (China Server)
 (https://server.growatt.com -&gt; https://openapi.growatt.com) (International Server)
 (https://server-us.growatt.com -&gt; https://openapi-us.growatt.com) (North America Server)
 (https://server.smten.com/ -&gt; https://openapi.smten.com) (Smart Server)
 http://ess-server.atesspower.com (Times Energy Server)
 http://openapi-au.growatt.com (Australia and New Zealand Users)

**Overall Description:**

- The interface supports http, see the interface definition for details.

- Use GET/POST, see the interface definition for details, parameters are utf-8 encoded, and processed with urlencode.

- All data is encoded in utf-8.

- Supports returning in json format.

- The return data structure is data: main content, code: error code, message: error message.

- When calling the interface, you need to add a token in the http header: the TOKEN obtained from applying to Growatt's OSS system.

- Time Format
  - Date format: YYYY-MM-DD, e.g., 2015-04-08
  - Time format: YYYY-MM-DD HH:mm:ss, e.g., 2015-04-03 00:01:00

- Example Images:
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=a52dcfac2a956a44f43b79ae226090e0&amp;file=file.png)

![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=27c6d417a40fd6e4c78d09728db2c09f&amp;file=file.png)

---

# 3. Modification Record

*Page ID: `11292913640068936`*

-  2024

|  Date | Modified by  | Modification Content |
| ------------ | ------------ | ------------ |
| 2024-06-21  | Bo Le  | Added Noah information |

-  2024

|  Date | Modified by  | Modification Content |
| ------------ | ------------ | ------------ |
| 2024-06-21  | Bo Le  | Added Australia address |

-  2024

|  Date | Modified by  | Modification Content |
| ------------ | ------------ | ------------ |
| 2024-05-22  | Zhu Xiaohai  | Document drafting |



**Remarks**
This interface is only for users who have OSS accounts and have applied for tokens. It mainly helps customers obtain real-time and historical data of devices under OSS.
1. The acquisition of API data is based on the relationship under OSS (if there is no device under the OSS account, it cannot be obtained)
2. Unable to obtain power station and user information under OSS
3. No need to specify tokens for terminal users
4. Temporarily unable to obtain device fault information (tentative)
5. Unable to remotely set device parameters (tentative)
6. Unable to register users and power stations (no addition, deletion, modification, or search of users and power stations)
7. Unable to add collectors (no addition, deletion, modification, or search of collectors)

---

# 4. Global Error Codes

*Page ID: `11292913883034530`*

| Error Code  | Error Description  |
| ------------ | ------------ |
|  0 | Normal |
|  1 | System Error |
|  2 | Invalid Secret Token |
|  3 | Device Permission Verification Failed |
|  4 | Device Not Found |
|  5 | Device Offline |
|  6 | Failed to Set Parameters |
|  7 | Device Type Error |
|  8 | Device SN is Empty |
|  9 | Date Cannot Be Empty |
|  10 | Page Number Cannot Be Empty |
|  11 | Device SN Exceeds Quantity Limit |
|  12 | No Permission to Access Device |
|  100 | API Access Interval |
|  101 | No Permission to Access |
|  102 | Access Frequency Limit, Different Interfaces Have Different Time Limits |
|  -1 | Please Use the New Domain for Access (https://server-cn.growatt.com-&gt;https://openapi-cn.growatt.com)(https://server.growatt.com-&gt;https://openapi.growatt.com)(https://server-us.growatt.com-&gt;https://openapi-us.growatt.com) |

---

# 5. Description of Device Types

*Page ID: `11292914311318022`*

**Brief Description:**
- Description of device types and specific models under each category

**Device Types:**
- inv (Description: Inverter)
- storage
- max
- sph
- spa
- min
- wit
- sph-s
- noah

**Specific Models under Each Device Type:**

- Off-grid Storage Inverter
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=7eb5c60a213de3b8680fc3a66f89891e&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:10.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} .font3 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; font-size:10.0pt; mso-generic-font-family:auto; mso-font-charset:134; background:#F9CBAA; mso-pattern:auto none; text-align:left;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} .et4 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et6 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center; white-space:normal;} --&gt;

- 
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=006370663eceb889d3e7871f42ebad13&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:10.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} .font3 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; font-size:10.0pt; mso-generic-font-family:auto; mso-font-charset:134; background:#FFF3CA; mso-pattern:auto none; text-align:left;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} .et4 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et6 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} --&gt;

- 
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=3149426bdf45bf03671d2ede97466909&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:10.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} .font3 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; font-size:10.0pt; mso-generic-font-family:auto; mso-font-charset:134; background:#E3F2D9; mso-pattern:auto none; text-align:left;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} .et4 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} --&gt;

- 
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=f678838f71fddca35fe9bdf884be95ca&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:10.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} .font3 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; font-size:10.0pt; mso-generic-font-family:auto; mso-font-charset:134; background:#D2F4F2; mso-pattern:auto none; text-align:left;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} .et4 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} --&gt;

- 
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=45aebb1ea2b4c31ac5e8d919e3cd5855&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; background:#FADADE; mso-pattern:auto none; text-align:center;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border-top:.5pt solid #000000; border-right:.5pt solid #000000; border-bottom:.5pt solid #000000; border-left:none; text-align:center;} .et4 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} --&gt;

- 
![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=d4a1e0e28723d81da3442d85e7c4c913&amp;file=file.png)   &lt;!--.font0 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font1 {color:#000000; font-size:10.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} .font2 {color:#000000; font-size:11.0pt; font-family:SimSun; font-weight:400; font-style:normal; text-decoration:none;} .font3 {color:#000000; font-size:11.0pt; font-family:宋体; font-weight:400; font-style:normal; text-decoration:none;} br {mso-data-placement:same-cell;} td {padding-top:1px; padding-left:1px; padding-right:1px; mso-ignore:padding; color:#000000; font-size:11.0pt; font-weight:400; font-style:normal; text-decoration:none; font-family:宋体; mso-generic-font-family:auto; mso-font-charset:134; mso-number-format:General; border:none; mso-background-source:auto; mso-pattern:auto; text-align:general; vertical-align:middle; white-space:nowrap; mso-rotate:0; mso-protection:locked visible;} .et2 {color:#000000; font-size:10.0pt; mso-generic-font-family:auto; mso-font-charset:134; background:#FEE796; mso-pattern:auto none; text-align:left;} .et3 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:center;} .et4 {color:#000000; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} .et5 {color:#000000; font-family:SimSun; mso-generic-font-family:auto; mso-font-charset:134; border:.5pt solid #000000; text-align:left;} --&gt;

- 

 ` NOAH 2000`



---

# 6. Device List

*Page ID: `11292915113214428`*

**Brief Description:**

- Retrieve the list of devices associated with the distributor, installer, and terminal account of the secret token. The devices obtained through this interface are the only ones allowed to fetch data from; devices not on the list are not permitted to retrieve data.

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryDeviceList`

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description   |
|:---------------|:---------|:-------|:--------------|
| token          | Yes      | String | Secret token  |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type | Description             |
|:---------------|:---------|:-----|:------------------------|
| page           | Yes      | int  | Page number, default 1 (1~n) |

**Example Call**

| Parameter Name | Required | Value | Description             |
|:---------------|:---------|:------|:------------------------|
| page           | Yes      | 1     | Page number, default 1  |

**Example Response**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;pages&quot;: 1,
        &quot;pageSize&quot;: 100,
        &quot;count&quot;: 7,
        &quot;other&quot;: null,
        &quot;notPager&quot;: false,
        &quot;data&quot;: [
            {
                &quot;deviceType&quot;: &quot;max&quot;,
                &quot;deviceSn&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;createDate&quot;: &quot;2021-06-29 12:02:46.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;AEC1733378&quot;,
                &quot;createDate&quot;: &quot;2018-11-10 16:42:59.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;CI04010115&quot;,
                &quot;createDate&quot;: &quot;2019-12-19 21:38:38.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;AEC173337D&quot;,
                &quot;createDate&quot;: &quot;2019-04-03 10:55:21.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;BX30911324&quot;,
                &quot;createDate&quot;: &quot;2020-07-09 11:01:04.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;PT44390040&quot;,
                &quot;createDate&quot;: &quot;2020-07-09 10:50:55.0&quot;
            },
            {
                &quot;deviceType&quot;: &quot;inv&quot;,
                &quot;deviceSn&quot;: &quot;PR34211399&quot;,
                &quot;createDate&quot;: &quot;2017-01-18 14:09:53.0&quot;
            }
        ],
        &quot;lastPager&quot;: true,
        &quot;startCount&quot;: 0
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Response Parameters Description**

| Parameter Name | Type   | Description                                                   |
|:---------------|:-------|:--------------------------------------------------------------|
| deviceType     | string | [Device Type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |
| count          | string | Device Count                                                  |
| deviceSn       | string | Device Serial Number                                          |
| datalogSn       | string | Collector Serial Number                                          |
| createDate     | string | Date Added                                                    |

**Remarks**

- Fetch frequency is limited to once every 5 seconds.

---

# 7. Batch device information

*Page ID: `11292915673945114`*

**Brief Description:**

- Retrieve basic information of devices in bulk based on device type and device SN. The data returned by the interface will only include devices that the key token has permission to access. Information about devices without permission will not be returned.
- `Device type refers to the deviceType parameter in the Get Device List interface.`

**Request URL:**
- ` https://openapi.growatt.com/v4/new-api/queryDeviceInfo `

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Descriptions:**

| Parameter Name | Required | Type   | Description                      |
|:---------------|:---------|:-------|:---------------------------------|
| token          | Yes      | String | Key token                        |

**HTTP Body Parameters and Descriptions:**

| Parameter Name | Required | Type   | Description                                                                 |
|:---------------|:---------|:-------|:----------------------------------------------------------------------------|
| deviceSn       | Yes      | string | Device SN (comma-separated list of device SNs), example: xxxxxxx,xxxxxxx,xxxxxxx (up to 100) |
| deviceType     | Yes      | string | [Device Type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |

**Example Call**

```json
{
  &quot;deviceSn&quot;: &quot;FDCJQ00003,FDCJQ00002&quot;,
  &quot;deviceType&quot;: &quot;min&quot;
}
```

**Example Response**

inv: https://www.showdoc.com.cn/2540838290984246/11292916280672808
storage: https://www.showdoc.com.cn/2540838290984246/11292917862205677
sph: https://www.showdoc.com.cn/2540838290984246/11292921698309783
max: https://www.showdoc.com.cn/2540838290984246/11292919260348864
spa: https://www.showdoc.com.cn/2540838290984246/11292923430103270
min: https://www.showdoc.com.cn/2540838290984246/11292925501705236
wit: https://www.showdoc.com.cn/2540838290984246/11292927244927496
sph-s: https://www.showdoc.com.cn/2540838290984246/11292929153206911
noah：https://www.showdoc.com.cn/2540838290984246/11315140426110613

**Notes**

- The retrieval frequency is once every 5 minutes.

---

# 8. Batch equipment data information

*Page ID: `11292915898375566`*

**Brief Description:**

- Retrieve the last detailed data for multiple devices based on their SN and device type. The interface returns data only for devices that the secret token has permission to access. Information for devices without permission will not be returned.

- `Data will only be returned for machines that were online starting from 2024-05-30.`

- `Device type corresponds to the deviceType parameter in the Get Device List API.`

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryLastData`

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description                  |
|:---------------|:---------|:-------|:-----------------------------|
| token          | Yes      | String | Secret token                 |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type   | Description                                                                                                          |
|:---------------|:---------|:-------|:---------------------------------------------------------------------------------------------------------------------|
| deviceType     | Yes      | String | [Device Type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;)                            |
| deviceSn       | Yes      | string | Inverter serial number (SN) array, maximum of 100, device serial number strings separated by commas, e.g., xxxx,xxxxx,xxxx (up to 100) |

Request Example:

![](https://www.showdoc.com.cn/server/api/attachment/visitFile?sign=03760d5fc014f5f1bd4d348a7330be1d&amp;file=file.png)

**Return Example**
inv:  https://www.showdoc.com.cn/2540838290984246/11292916843107127
storage: https://www.showdoc.com.cn/2540838290984246/11292918042831939
sph:  https://www.showdoc.com.cn/2540838290984246/11292922052386278
max: https://www.showdoc.com.cn/2540838290984246/11292919843180935
spa: https://www.showdoc.com.cn/2540838290984246/11292924339104189
min: https://www.showdoc.com.cn/2540838290984246/11292926445680439
wit：https://www.showdoc.com.cn/2540838290984246/11292928051977434
sph-s: https://www.showdoc.com.cn/2540838290984246/11292929836439932
noah：https://www.showdoc.com.cn/2540838290984246/11315141402697236

**Remarks**

- The retrieval frequency is once every 5 minutes.
- Note: Due to their special nature, noah-type machines have a frequency of once every minute.

**Return Format Example:**
``` 
{
    &quot;error_msg&quot;: &quot;&quot;,
    &quot;data&quot;: {
        &quot;UMJ0CC4025&quot;: {
            &quot;vPidPvcpe&quot;: 0,
            &quot;realOPPercent&quot;: 0,
            &quot;warnCode&quot;: 0,
            &quot;epv5Today&quot;: 36,
            &quot;pacr&quot;: 9744.4,
            &quot;epv13Today&quot;: 0,
            &quot;pacs&quot;: 9967.3,
            &quot;rac&quot;: 0,
            &quot;epv13Total&quot;: 0,
            &quot;pact&quot;: 10083,
            &quot;epvTotal&quot;: 487302.4,
            &quot;pBusVoltage&quot;: 389.20001220703125,
            &quot;deratingMode&quot;: 0,
            &quot;epv5Total&quot;: 60729.3,
            &quot;debug3&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
            &quot;vString8&quot;: 759.2000122070312,
            &quot;vString7&quot;: 759.2000122070312,
            &quot;vString9&quot;: 767.7999877929688,
            &quot;pidStatus&quot;: 0,
            &quot;iPidPvepe&quot;: 0,
            &quot;vString2&quot;: 783.6000366210938,
            &quot;dwStringWarningValue1&quot;: 0,
            &quot;vString1&quot;: 783.6000366210938,
            &quot;vString4&quot;: 767,
            &quot;pidStatusText&quot;: &quot;Lost&quot;,
            &quot;vString3&quot;: 767,
            &quot;vString6&quot;: 751.1000366210938,
            &quot;vString5&quot;: 751.1000366210938,
            &quot;reactPowerMax&quot;: 0,
            &quot;epv11Today&quot;: 0,
            &quot;vPidPvbpe&quot;: 0,
            &quot;nBusVoltage&quot;: 389.8000183105469,
            &quot;ppv2&quot;: 3501.9,
            &quot;ppv3&quot;: 3601.4,
            &quot;ppv4&quot;: 3692.1,
            &quot;ppv5&quot;: 3455.1,
            &quot;compqt&quot;: 0,
            &quot;compqs&quot;: 0,
            &quot;epv11Total&quot;: 0,
            &quot;compqr&quot;: 0,
            &quot;ppv1&quot;: 3460.6,
            &quot;temperature&quot;: 21.5,
            &quot;debug1&quot;: &quot;0，0，0，320，32998，0，7762，7762&quot;,
            &quot;debug2&quot;: &quot;0，0，0，0，0，11000，18390，7&quot;,
            &quot;calendar&quot;: {
                &quot;calendarType&quot;: &quot;gregory&quot;,
                &quot;firstDayOfWeek&quot;: 1,
                &quot;minimalDaysInFirstWeek&quot;: 1,
                &quot;gregorianChange&quot;: {
                    &quot;date&quot;: 15,
                    &quot;hours&quot;: 8,
                    &quot;seconds&quot;: 0,
                    &quot;month&quot;: 9,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: -318,
                    &quot;minutes&quot;: 0,
                    &quot;time&quot;: -12219292800000,
                    &quot;day&quot;: 5
                },
                &quot;timeZone&quot;: {
                    &quot;dirty&quot;: false,
                    &quot;lastRuleInstance&quot;: null,
                    &quot;DSTSavings&quot;: 0,
                    &quot;displayName&quot;: &quot;中国标准时间&quot;,
                    &quot;rawOffset&quot;: 28800000,
                    &quot;ID&quot;: &quot;Asia/Shanghai&quot;
                },
                &quot;weekYear&quot;: 2024,
                &quot;time&quot;: {
                    &quot;date&quot;: 29,
                    &quot;hours&quot;: 15,
                    &quot;seconds&quot;: 3,
                    &quot;month&quot;: 1,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: 124,
                    &quot;minutes&quot;: 31,
                    &quot;time&quot;: 1709191863943,
                    &quot;day&quot;: 4
                },
                &quot;timeInMillis&quot;: 1709191863943,
                &quot;weeksInWeekYear&quot;: 52,
                &quot;lenient&quot;: true,
                &quot;weekDateSupported&quot;: true
            },
            &quot;sDci&quot;: 7.5,
            &quot;address&quot;: 0,
            &quot;epv7Today&quot;: 18.4,
            &quot;epv1Today&quot;: 36.5,
            &quot;epv7Total&quot;: 31450.1,
            &quot;epv1Total&quot;: 61113,
            &quot;vact&quot;: 241.8000030517578,
            &quot;vacs&quot;: 239.60000610351562,
            &quot;vacr&quot;: 241.1999969482422,
            &quot;iPidPvdpe&quot;: 0,
            &quot;ppv&quot;: 29441.1,
            &quot;wPIDFaultValue&quot;: 0,
            &quot;ctqt&quot;: 0,
            &quot;ctqr&quot;: 0,
            &quot;dataLogSn&quot;: &quot;&quot;,
            &quot;ctqs&quot;: 0,
            &quot;vpv3&quot;: 750.2999877929688,
            &quot;vpv2&quot;: 761.2999877929688,
            &quot;vpv1&quot;: 786.5,
            &quot;tDci&quot;: 55.79999923706055,
            &quot;vPidPvepe&quot;: 0,
            &quot;apfStatus&quot;: 0,
            &quot;vpv9&quot;: 760.4000244140625,
            &quot;vpv8&quot;: 758.2000122070312,
            &quot;vpv7&quot;: 755.2000122070312,
            &quot;vpv6&quot;: 756.4000244140625,
            &quot;vpv5&quot;: 767.7999877929688,
            &quot;vpv4&quot;: 753.5,
            &quot;vpv16&quot;: 0,
            &quot;pac&quot;: 28952.7,
            &quot;vpv15&quot;: 0,
            &quot;powerTotal&quot;: 0,
            &quot;powerToday&quot;: 0,
            &quot;pidFaultCode&quot;: 0,
            &quot;vString32&quot;: 0,
            &quot;vString31&quot;: 0,
            &quot;vString30&quot;: 0,
            &quot;vpv10&quot;: 751.9000244140625,
            &quot;vpv14&quot;: 0,
            &quot;vpv13&quot;: 0,
            &quot;vpv12&quot;: 0,
            &quot;vpv11&quot;: 0,
            &quot;iPidPvcpe&quot;: 0,
            &quot;ppv6&quot;: 4160.2,
            &quot;ppv7&quot;: 1963.5,
            &quot;ppv8&quot;: 1819.6,
            &quot;ppv9&quot;: 1901,
            &quot;epv3Total&quot;: 60169.5,
            &quot;epv3Today&quot;: 35.8,
            &quot;vPidPvdpe&quot;: 0,
            &quot;vString22&quot;: 0,
            &quot;vString21&quot;: 0,
            &quot;vString20&quot;: 751.9000244140625,
            &quot;vString26&quot;: 0,
            &quot;epv9Today&quot;: 17.7,
            &quot;vString25&quot;: 0,
            &quot;vPidPvpe15&quot;: 0,
            &quot;vString24&quot;: 0,
            &quot;vPidPvpe16&quot;: 0,
            &quot;vString23&quot;: 0,
            &quot;epv9Total&quot;: 30535.2,
            &quot;vPidPvpe13&quot;: 0,
            &quot;vPidPvpe14&quot;: 0,
            &quot;vString29&quot;: 0,
            &quot;vPidPvpe11&quot;: 0,
            &quot;vString28&quot;: 0,
            &quot;vPidPvpe12&quot;: 0,
            &quot;vString27&quot;: 0,
            &quot;afciStatus&quot;: 0,
            &quot;epv8Today&quot;: 17.2,
            &quot;epv8Total&quot;: 29432.6,
            &quot;vPidPvpe10&quot;: 0,
            &quot;epv2Today&quot;: 35.1,
            &quot;epv2Total&quot;: 60326.1,
            &quot;iPidPvpe13&quot;: 0,
            &quot;iPidPvpe12&quot;: 0,
            &quot;iPidPvpe11&quot;: 0,
            &quot;iPidPvpe10&quot;: -0.10000000149011612,
            &quot;iPidPvpe16&quot;: 0,
            &quot;timeCalendar&quot;: {
                &quot;calendarType&quot;: &quot;gregory&quot;,
                &quot;firstDayOfWeek&quot;: 1,
                &quot;minimalDaysInFirstWeek&quot;: 1,
                &quot;gregorianChange&quot;: {
                    &quot;date&quot;: 15,
                    &quot;hours&quot;: 8,
                    &quot;seconds&quot;: 0,
                    &quot;month&quot;: 9,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: -318,
                    &quot;minutes&quot;: 0,
                    &quot;time&quot;: -12219292800000,
                    &quot;day&quot;: 5
                },
                &quot;timeZone&quot;: {
                    &quot;dirty&quot;: false,
                    &quot;lastRuleInstance&quot;: null,
                    &quot;DSTSavings&quot;: 0,
                    &quot;displayName&quot;: &quot;中国标准时间&quot;,
                    &quot;rawOffset&quot;: 28800000,
                    &quot;ID&quot;: &quot;Asia/Shanghai&quot;
                },
                &quot;weekYear&quot;: 2024,
                &quot;time&quot;: {
                    &quot;date&quot;: 29,
                    &quot;hours&quot;: 15,
                    &quot;seconds&quot;: 3,
                    &quot;month&quot;: 1,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: 124,
                    &quot;minutes&quot;: 31,
                    &quot;time&quot;: 1709191863943,
                    &quot;day&quot;: 4
                },
                &quot;timeInMillis&quot;: 1709191863943,
                &quot;weeksInWeekYear&quot;: 52,
                &quot;lenient&quot;: true,
                &quot;weekDateSupported&quot;: true
            },
            &quot;iPidPvpe15&quot;: 0,
            &quot;iPidPvpe14&quot;: 0,
            &quot;vString11&quot;: 756.7999877929688,
            &quot;vString10&quot;: 767.7999877929688,
            &quot;again&quot;: false,
            &quot;vString15&quot;: 757.2000122070312,
            &quot;vString14&quot;: 760,
            &quot;vString13&quot;: 760,
            &quot;eacTotal&quot;: 276507.5,
            &quot;vString12&quot;: 756.7999877929688,
            &quot;eacToday&quot;: 286.1,
            &quot;vString19&quot;: 751.9000244140625,
            &quot;vString18&quot;: 760.4000244140625,
            &quot;vString17&quot;: 760.4000244140625,
            &quot;iPidPvbpe&quot;: 0,
            &quot;vString16&quot;: 757.2000122070312,
            &quot;faultCode2&quot;: 0,
            &quot;faultCode1&quot;: 0,
            &quot;epv12Total&quot;: 0,
            &quot;statusText&quot;: &quot;Normal&quot;,
            &quot;epv12Today&quot;: 0,
            &quot;time&quot;: &quot;2024-02-29 15:31:03&quot;,
            &quot;pvIso&quot;: 1264,
            &quot;epv14Total&quot;: 0,
            &quot;epv6Total&quot;: 63577.8,
            &quot;epv14Today&quot;: 0,
            &quot;fac&quot;: 49.96999740600586,
            &quot;epv6Today&quot;: 38.3,
            &quot;lost&quot;: true,
            &quot;vacTr&quot;: 418.8999938964844,
            &quot;id&quot;: 0,
            &quot;serialNum&quot;: &quot;UMJ0CC4025&quot;,
            &quot;wStringStatusValue&quot;: 0,
            &quot;temperature5&quot;: 18.399999618530273,
            &quot;epv16Total&quot;: 0,
            &quot;temperature4&quot;: 0,
            &quot;epv16Today&quot;: 0,
            &quot;iPidPvape&quot;: 0,
            &quot;eRacToday&quot;: 0,
            &quot;eRacTotal&quot;: 0,
            &quot;vacSt&quot;: 414.8999938964844,
            &quot;vPidPvgpe&quot;: 0,
            &quot;status&quot;: 1,
            &quot;ppv15&quot;: 0,
            &quot;ppv16&quot;: 0,
            &quot;ppv13&quot;: 0,
            &quot;ppv14&quot;: 0,
            &quot;ppv11&quot;: 0,
            &quot;ppv12&quot;: 0,
            &quot;ppv10&quot;: 1879.7,
            &quot;strUnblance&quot;: 0,
            &quot;afciPv1&quot;: 0,
            &quot;afciPv2&quot;: 0,
            &quot;ctharis&quot;: 0,
            &quot;ctharit&quot;: 0,
            &quot;ctharir&quot;: 0,
            &quot;temperature3&quot;: 14.90000057220459,
            &quot;epv10Today&quot;: 17.9,
            &quot;temperature2&quot;: 19,
            &quot;epv10Total&quot;: 30105.7,
            &quot;reactPower&quot;: 0,
            &quot;withTime&quot;: false,
            &quot;ipv16&quot;: 0,
            &quot;epv4Total&quot;: 59863.1,
            &quot;epv4Today&quot;: 36.8,
            &quot;ipv12&quot;: 0,
            &quot;ipv13&quot;: 0,
            &quot;ipv14&quot;: 0,
            &quot;ipv15&quot;: 0,
            &quot;ctit&quot;: 0,
            &quot;ipv10&quot;: 2.5,
            &quot;ipv11&quot;: 0,
            &quot;maxBean&quot;: null,
            &quot;vPidPvpe9&quot;: 0,
            &quot;ctir&quot;: 0,
            &quot;iPidPvhpe&quot;: 0,
            &quot;ctis&quot;: 0,
            &quot;faultValue&quot;: 0,
            &quot;vPidPvfpe&quot;: 0,
            &quot;strFault&quot;: 0,
            &quot;vPidPvape&quot;: 0,
            &quot;currentString32&quot;: 0,
            &quot;currentString31&quot;: 0,
            &quot;currentString30&quot;: 0,
            &quot;currentString1&quot;: 2.200000047683716,
            &quot;strBreak&quot;: 0,
            &quot;currentString5&quot;: 2.6000001430511475,
            &quot;currentString4&quot;: 1.899999976158142,
            &quot;currentString3&quot;: 2.6000001430511475,
            &quot;currentString2&quot;: 2.1000001430511475,
            &quot;currentString9&quot;: 2.9000000953674316,
            &quot;currentString8&quot;: 2.1000001430511475,
            &quot;day&quot;: &quot;&quot;,
            &quot;currentString7&quot;: 2.700000047683716,
            &quot;currentString6&quot;: 2.299999952316284,
            &quot;apfStatusText&quot;: &quot;None&quot;,
            &quot;warnBit&quot;: 0,
            &quot;reactPowerTotal&quot;: 0,
            &quot;gfci&quot;: 1,
            &quot;iPidPvgpe&quot;: 0,
            &quot;iacr&quot;: 40.400001525878906,
            &quot;iact&quot;: 41.70000076293945,
            &quot;iacs&quot;: 41.60000228881836,
            &quot;currentString16&quot;: 0,
            &quot;warningValue2&quot;: 0,
            &quot;currentString15&quot;: 2.799999952316284,
            &quot;strUnmatch&quot;: 0,
            &quot;warningValue1&quot;: 0,
            &quot;currentString14&quot;: 0,
            &quot;currentString13&quot;: 2.700000047683716,
            &quot;warningValue3&quot;: 0,
            &quot;currentString12&quot;: 2.5,
            &quot;currentString11&quot;: 2.799999952316284,
            &quot;currentString10&quot;: 1.600000023841858,
            &quot;rDci&quot;: 9.300000190734863,
            &quot;ipv2&quot;: 4.599999904632568,
            &quot;opFullwatt&quot;: 0,
            &quot;ipv1&quot;: 4.400000095367432,
            &quot;ipv4&quot;: 4.900000095367432,
            &quot;ipv3&quot;: 4.800000190734863,
            &quot;vacRs&quot;: 417.3999938964844,
            &quot;ipv6&quot;: 5.5,
            &quot;ipv5&quot;: 4.5,
            &quot;ipv8&quot;: 2.4000000953674316,
            &quot;alias&quot;: &quot;&quot;,
            &quot;faultType&quot;: 0,
            &quot;ipv7&quot;: 2.6000001430511475,
            &quot;ipv9&quot;: 2.5,
            &quot;currentString19&quot;: 2.6000001430511475,
            &quot;currentString18&quot;: 0,
            &quot;currentString17&quot;: 2.700000047683716,
            &quot;currentString27&quot;: 0,
            &quot;currentString26&quot;: 0,
            &quot;pidBus&quot;: 3.5,
            &quot;currentString25&quot;: 0,
            &quot;currentString24&quot;: 0,
            &quot;currentString23&quot;: 0,
            &quot;currentString22&quot;: 0,
            &quot;timeTotal&quot;: 3.15978825E7,
            &quot;currentString21&quot;: 0,
            &quot;currentString20&quot;: 0,
            &quot;ipmTemperature&quot;: 0,
            &quot;compharis&quot;: 0,
            &quot;iPidPvfpe&quot;: 0,
            &quot;compharit&quot;: 0,
            &quot;compharir&quot;: 0,
            &quot;pf&quot;: 1,
            &quot;epv15Today&quot;: 0,
            &quot;vPidPvhpe&quot;: 0,
            &quot;iPidPvpe9&quot;: 0,
            &quot;currentString29&quot;: 0,
            &quot;currentString28&quot;: 0,
            &quot;epv15Total&quot;: 0
        },
        &quot;UMJ0CC4022&quot;: {
            &quot;vPidPvcpe&quot;: 0,
            &quot;realOPPercent&quot;: 0,
            &quot;warnCode&quot;: 0,
            &quot;epv5Today&quot;: 19.6,
            &quot;pacr&quot;: 11532.4,
            &quot;epv13Today&quot;: 0,
            &quot;pacs&quot;: 11548.8,
            &quot;rac&quot;: 0,
            &quot;epv13Total&quot;: 0,
            &quot;pact&quot;: 11591.8,
            &quot;epvTotal&quot;: 453177.1,
            &quot;pBusVoltage&quot;: 397.8000183105469,
            &quot;deratingMode&quot;: 0,
            &quot;epv5Total&quot;: 33140.8,
            &quot;debug3&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
            &quot;vString8&quot;: 766.2999877929688,
            &quot;vString7&quot;: 766.2999877929688,
            &quot;vString9&quot;: 753.2000122070312,
            &quot;pidStatus&quot;: 0,
            &quot;iPidPvepe&quot;: 0,
            &quot;vString2&quot;: 759.6000366210938,
            &quot;dwStringWarningValue1&quot;: 0,
            &quot;vString1&quot;: 759.6000366210938,
            &quot;vString4&quot;: 752.6000366210938,
            &quot;pidStatusText&quot;: &quot;Lost&quot;,
            &quot;vString3&quot;: 752.6000366210938,
            &quot;vString6&quot;: 739.1000366210938,
            &quot;vString5&quot;: 739.1000366210938,
            &quot;reactPowerMax&quot;: 0,
            &quot;epv11Today&quot;: 0,
            &quot;vPidPvbpe&quot;: 0,
            &quot;nBusVoltage&quot;: 396.6000061035156,
            &quot;ppv2&quot;: 5109.5,
            &quot;ppv3&quot;: 4978.1,
            &quot;ppv4&quot;: 5138.2,
            &quot;ppv5&quot;: 2560.2,
            &quot;compqt&quot;: 0,
            &quot;compqs&quot;: 0,
            &quot;epv11Total&quot;: 0,
            &quot;compqr&quot;: 0,
            &quot;ppv1&quot;: 4934.1,
            &quot;temperature&quot;: 22,
            &quot;debug1&quot;: &quot;0，0，0，320，32998，0，7533，7936&quot;,
            &quot;debug2&quot;: &quot;0，0，0，0，0，11000，18390，107&quot;,
            &quot;calendar&quot;: {
                &quot;calendarType&quot;: &quot;gregory&quot;,
                &quot;firstDayOfWeek&quot;: 1,
                &quot;minimalDaysInFirstWeek&quot;: 1,
                &quot;gregorianChange&quot;: {
                    &quot;date&quot;: 15,
                    &quot;hours&quot;: 8,
                    &quot;seconds&quot;: 0,
                    &quot;month&quot;: 9,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: -318,
                    &quot;minutes&quot;: 0,
                    &quot;time&quot;: -12219292800000,
                    &quot;day&quot;: 5
                },
                &quot;timeZone&quot;: {
                    &quot;dirty&quot;: false,
                    &quot;lastRuleInstance&quot;: null,
                    &quot;DSTSavings&quot;: 0,
                    &quot;displayName&quot;: &quot;中国标准时间&quot;,
                    &quot;rawOffset&quot;: 28800000,
                    &quot;ID&quot;: &quot;Asia/Shanghai&quot;
                },
                &quot;weekYear&quot;: 2024,
                &quot;time&quot;: {
                    &quot;date&quot;: 29,
                    &quot;hours&quot;: 15,
                    &quot;seconds&quot;: 4,
                    &quot;month&quot;: 1,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: 124,
                    &quot;minutes&quot;: 33,
                    &quot;time&quot;: 1709191984675,
                    &quot;day&quot;: 4
                },
                &quot;timeInMillis&quot;: 1709191984675,
                &quot;weeksInWeekYear&quot;: 52,
                &quot;lenient&quot;: true,
                &quot;weekDateSupported&quot;: true
            },
            &quot;sDci&quot;: 87.5,
            &quot;address&quot;: 0,
            &quot;epv7Today&quot;: 18.9,
            &quot;epv1Today&quot;: 38.3,
            &quot;epv7Total&quot;: 31396,
            &quot;epv1Total&quot;: 64860.4,
            &quot;vact&quot;: 242,
            &quot;vacs&quot;: 240.60000610351562,
            &quot;vacr&quot;: 243.3000030517578,
            &quot;iPidPvdpe&quot;: 0,
            &quot;ppv&quot;: 34983.7,
            &quot;wPIDFaultValue&quot;: 0,
            &quot;ctqt&quot;: 0,
            &quot;ctqr&quot;: 0,
            &quot;dataLogSn&quot;: &quot;&quot;,
            &quot;ctqs&quot;: 0,
            &quot;vpv3&quot;: 743,
            &quot;vpv2&quot;: 751.4000244140625,
            &quot;vpv1&quot;: 759.1000366210938,
            &quot;tDci&quot;: 30.5,
            &quot;vPidPvepe&quot;: 0,
            &quot;apfStatus&quot;: 0,
            &quot;vpv9&quot;: 742.7999877929688,
            &quot;vpv8&quot;: 750.7999877929688,
            &quot;vpv7&quot;: 747.6000366210938,
            &quot;vpv6&quot;: 739.9000244140625,
            &quot;vpv5&quot;: 753,
            &quot;vpv4&quot;: 766.9000244140625,
            &quot;vpv16&quot;: 0,
            &quot;pac&quot;: 34260.4,
            &quot;vpv15&quot;: 0,
            &quot;powerTotal&quot;: 0,
            &quot;powerToday&quot;: 0,
            &quot;pidFaultCode&quot;: 0,
            &quot;vString32&quot;: 0,
            &quot;vString31&quot;: 0,
            &quot;vString30&quot;: 0,
            &quot;vpv10&quot;: 746.9000244140625,
            &quot;vpv14&quot;: 0,
            &quot;vpv13&quot;: 0,
            &quot;vpv12&quot;: 0,
            &quot;vpv11&quot;: 0,
            &quot;iPidPvcpe&quot;: 0,
            &quot;ppv6&quot;: 2441.6,
            &quot;ppv7&quot;: 2467,
            &quot;ppv8&quot;: 2402.5,
            &quot;ppv9&quot;: 2451.2,
            &quot;epv3Total&quot;: 63851.9,
            &quot;epv3Today&quot;: 37.9,
            &quot;vPidPvdpe&quot;: 0,
            &quot;vString22&quot;: 0,
            &quot;vString21&quot;: 0,
            &quot;vString20&quot;: 746.9000244140625,
            &quot;vString26&quot;: 0,
            &quot;epv9Today&quot;: 18.8,
            &quot;vString25&quot;: 0,
            &quot;vPidPvpe15&quot;: 0,
            &quot;vString24&quot;: 0,
            &quot;vPidPvpe16&quot;: 0,
            &quot;vString23&quot;: 0,
            &quot;epv9Total&quot;: 32554.7,
            &quot;vPidPvpe13&quot;: 0,
            &quot;vPidPvpe14&quot;: 0,
            &quot;vString29&quot;: 0,
            &quot;vPidPvpe11&quot;: 0,
            &quot;vString28&quot;: 0,
            &quot;vPidPvpe12&quot;: 0,
            &quot;vString27&quot;: 0,
            &quot;afciStatus&quot;: 0,
            &quot;epv8Today&quot;: 18.8,
            &quot;epv8Total&quot;: 30979.5,
            &quot;vPidPvpe10&quot;: 0,
            &quot;epv2Today&quot;: 38.9,
            &quot;epv2Total&quot;: 66099.9,
            &quot;iPidPvpe13&quot;: 0,
            &quot;iPidPvpe12&quot;: 0,
            &quot;iPidPvpe11&quot;: 0,
            &quot;iPidPvpe10&quot;: -0.10000000149011612,
            &quot;iPidPvpe16&quot;: 0,
            &quot;timeCalendar&quot;: {
                &quot;calendarType&quot;: &quot;gregory&quot;,
                &quot;firstDayOfWeek&quot;: 1,
                &quot;minimalDaysInFirstWeek&quot;: 1,
                &quot;gregorianChange&quot;: {
                    &quot;date&quot;: 15,
                    &quot;hours&quot;: 8,
                    &quot;seconds&quot;: 0,
                    &quot;month&quot;: 9,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: -318,
                    &quot;minutes&quot;: 0,
                    &quot;time&quot;: -12219292800000,
                    &quot;day&quot;: 5
                },
                &quot;timeZone&quot;: {
                    &quot;dirty&quot;: false,
                    &quot;lastRuleInstance&quot;: null,
                    &quot;DSTSavings&quot;: 0,
                    &quot;displayName&quot;: &quot;中国标准时间&quot;,
                    &quot;rawOffset&quot;: 28800000,
                    &quot;ID&quot;: &quot;Asia/Shanghai&quot;
                },
                &quot;weekYear&quot;: 2024,
                &quot;time&quot;: {
                    &quot;date&quot;: 29,
                    &quot;hours&quot;: 15,
                    &quot;seconds&quot;: 4,
                    &quot;month&quot;: 1,
                    &quot;timezoneOffset&quot;: -480,
                    &quot;year&quot;: 124,
                    &quot;minutes&quot;: 33,
                    &quot;time&quot;: 1709191984675,
                    &quot;day&quot;: 4
                },
                &quot;timeInMillis&quot;: 1709191984675,
                &quot;weeksInWeekYear&quot;: 52,
                &quot;lenient&quot;: true,
                &quot;weekDateSupported&quot;: true
            },
            &quot;iPidPvpe15&quot;: 0,
            &quot;iPidPvpe14&quot;: 0,
            &quot;vString11&quot;: 740.1000366210938,
            &quot;vString10&quot;: 753.2000122070312,
            &quot;again&quot;: false,
            &quot;vString15&quot;: 748.5,
            &quot;vString14&quot;: 750.6000366210938,
            &quot;vString13&quot;: 750.6000366210938,
            &quot;eacTotal&quot;: 255544.3,
            &quot;vString12&quot;: 740.1000366210938,
            &quot;eacToday&quot;: 265.4,
            &quot;vString19&quot;: 746.9000244140625,
            &quot;vString18&quot;: 742.7999877929688,
            &quot;vString17&quot;: 742.7999877929688,
            &quot;iPidPvbpe&quot;: 0,
            &quot;vString16&quot;: 748.5,
            &quot;faultCode2&quot;: 0,
            &quot;faultCode1&quot;: 0,
            &quot;epv12Total&quot;: 0,
            &quot;statusText&quot;: &quot;Normal&quot;,
            &quot;epv12Today&quot;: 0,
            &quot;time&quot;: &quot;2024-02-29 15:33:04&quot;,
            &quot;pvIso&quot;: 1744,
            &quot;epv14Total&quot;: 0,
            &quot;epv6Total&quot;: 31925.1,
            &quot;epv14Today&quot;: 0,
            &quot;fac&quot;: 49.98999786376953,
            &quot;epv6Today&quot;: 19,
            &quot;lost&quot;: true,
            &quot;vacTr&quot;: 418.8999938964844,
            &quot;id&quot;: 0,
            &quot;serialNum&quot;: &quot;UMJ0CC4022&quot;,
            &quot;wStringStatusValue&quot;: 0,
            &quot;temperature5&quot;: 18.100000381469727,
            &quot;epv16Total&quot;: 0,
            &quot;temperature4&quot;: 0,
            &quot;epv16Today&quot;: 0,
            &quot;iPidPvape&quot;: 0,
            &quot;eRacToday&quot;: 0,
            &quot;eRacTotal&quot;: 0,
            &quot;vacSt&quot;: 417.6000061035156,
            &quot;vPidPvgpe&quot;: 0,
            &quot;status&quot;: 1,
            &quot;ppv15&quot;: 0,
            &quot;ppv16&quot;: 0,
            &quot;ppv13&quot;: 0,
            &quot;ppv14&quot;: 0,
            &quot;ppv11&quot;: 0,
            &quot;ppv12&quot;: 0,
            &quot;ppv10&quot;: 2464.7,
            &quot;strUnblance&quot;: 0,
            &quot;afciPv1&quot;: 0,
            &quot;afciPv2&quot;: 0,
            &quot;ctharis&quot;: 0,
            &quot;ctharit&quot;: 0,
            &quot;ctharir&quot;: 0,
            &quot;temperature3&quot;: 17.5,
            &quot;epv10Today&quot;: 19.1,
            &quot;temperature2&quot;: 21.5,
            &quot;epv10Total&quot;: 32058.5,
            &quot;reactPower&quot;: 0,
            &quot;withTime&quot;: false,
            &quot;ipv16&quot;: 0,
            &quot;epv4Total&quot;: 66310.3,
            &quot;epv4Today&quot;: 39.2,
            &quot;ipv12&quot;: 0,
            &quot;ipv13&quot;: 0,
            &quot;ipv14&quot;: 0,
            &quot;ipv15&quot;: 0,
            &quot;ctit&quot;: 0,
            &quot;ipv10&quot;: 3.299999952316284,
            &quot;ipv11&quot;: 0,
            &quot;maxBean&quot;: null,
            &quot;vPidPvpe9&quot;: 0,
            &quot;ctir&quot;: 0,
            &quot;iPidPvhpe&quot;: 0,
            &quot;ctis&quot;: 0,
            &quot;faultValue&quot;: 0,
            &quot;vPidPvfpe&quot;: 0,
            &quot;strFault&quot;: 0,
            &quot;vPidPvape&quot;: 0,
            &quot;currentString32&quot;: 0,
            &quot;currentString31&quot;: 0,
            &quot;currentString30&quot;: 0,
            &quot;currentString1&quot;: 3.4000000953674316,
            &quot;strBreak&quot;: 0,
            &quot;currentString5&quot;: 3.6000001430511475,
            &quot;currentString4&quot;: 3.299999952316284,
            &quot;currentString3&quot;: 3.5,
            &quot;currentString2&quot;: 3,
            &quot;currentString9&quot;: 3.6000001430511475,
            &quot;currentString8&quot;: 3.4000000953674316,
            &quot;day&quot;: &quot;&quot;,
            &quot;currentString7&quot;: 3.4000000953674316,
            &quot;currentString6&quot;: 3.5,
            &quot;apfStatusText&quot;: &quot;None&quot;,
            &quot;warnBit&quot;: 0,
            &quot;reactPowerTotal&quot;: 0,
            &quot;gfci&quot;: 2,
            &quot;iPidPvgpe&quot;: 0,
            &quot;iacr&quot;: 47.400001525878906,
            &quot;iact&quot;: 47.900001525878906,
            &quot;iacs&quot;: 48,
            &quot;currentString16&quot;: 0,
            &quot;warningValue2&quot;: 0,
            &quot;currentString15&quot;: 3.5,
            &quot;strUnmatch&quot;: 0,
            &quot;warningValue1&quot;: 0,
            &quot;currentString14&quot;: 0,
            &quot;currentString13&quot;: 3.5,
            &quot;warningValue3&quot;: 0,
            &quot;currentString12&quot;: 0,
            &quot;currentString11&quot;: 3.5,
            &quot;currentString10&quot;: 0,
            &quot;rDci&quot;: 22.700000762939453,
            &quot;ipv2&quot;: 6.800000190734863,
            &quot;opFullwatt&quot;: 0,
            &quot;ipv1&quot;: 6.5,
            &quot;ipv4&quot;: 6.700000286102295,
            &quot;ipv3&quot;: 6.700000286102295,
            &quot;vacRs&quot;: 420.6000061035156,
            &quot;ipv6&quot;: 3.299999952316284,
            &quot;ipv5&quot;: 3.4000000953674316,
            &quot;ipv8&quot;: 3.200000047683716,
            &quot;alias&quot;: &quot;&quot;,
            &quot;faultType&quot;: 0,
            &quot;ipv7&quot;: 3.299999952316284,
            &quot;ipv9&quot;: 3.299999952316284,
            &quot;currentString19&quot;: 3.299999952316284,
            &quot;currentString18&quot;: 0,
            &quot;currentString17&quot;: 3.700000047683716,
            &quot;currentString27&quot;: 0,
            &quot;currentString26&quot;: 0,
            &quot;pidBus&quot;: 3.1000001430511475,
            &quot;currentString25&quot;: 0,
            &quot;currentString24&quot;: 0,
            &quot;currentString23&quot;: 0,
            &quot;currentString22&quot;: 0,
            &quot;timeTotal&quot;: 3.1484573E7,
            &quot;currentString21&quot;: 0,
            &quot;currentString20&quot;: 0,
            &quot;ipmTemperature&quot;: 0,
            &quot;compharis&quot;: 0,
            &quot;iPidPvfpe&quot;: 0,
            &quot;compharit&quot;: 0,
            &quot;compharir&quot;: 0,
            &quot;pf&quot;: 1,
            &quot;epv15Today&quot;: 0,
            &quot;vPidPvhpe&quot;: 0,
            &quot;iPidPvpe9&quot;: 0,
            &quot;currentString29&quot;: 0,
            &quot;currentString28&quot;: 0,
            &quot;epv15Total&quot;: 0
        }
    },
    &quot;error_code&quot;: 0
}
```

 **Remarks**

- The retrieval frequency is once every 5 minutes.




---

# 9. One day data

*Page ID: `11292916022305414`*

**Brief Description:**

- Retrieves all detailed data for a specific device on a particular day based on the device SN, device type, and date. The interface returns data only for devices that the secret token has permission to access. Information for devices without permission will not be returned.
- `The device type corresponds to the deviceType parameter in the fetch device list interface.`

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryHistoricalData`

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description                  |
|:---------------|:---------|:-------|:-----------------------------|
| token          | Yes      | String | Secret token                 |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type   | Description                              |
|:---------------|:---------|:-------|:-----------------------------------------|
| deviceSn       | Yes      | String | Device unique serial number (SN)         |
| deviceType     | Yes      | String | [Device type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |
| date           | Yes      | String | Start date (format: yyyy-mm-dd) Example: 2024-05-14 |

**Example Call**

```
{
  &quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
  &quot;deviceType&quot;: &quot;min&quot;,
  &quot;date&quot;: &quot;2024-05-14&quot;
}
```

**Example Response**

inv:   https://www.showdoc.com.cn/2540838290984246/11292917584269311
storage: https://www.showdoc.com.cn/2540838290984246/11292918959841019
sph:  https://www.showdoc.com.cn/2540838290984246/11292922712705121
max: https://www.showdoc.com.cn/2540838290984246/11292920771207078
spa: https://www.showdoc.com.cn/2540838290984246/11292925068299407
min: https://www.showdoc.com.cn/2540838290984246/11292926895869382
wit: https://www.showdoc.com.cn/2540838290984246/11292928841081078
sph-s: https://www.showdoc.com.cn/2540838290984246/11292930141133325
noah：https://www.showdoc.com.cn/2540838290984246/11315142054122408

**Notes**

- Retrieval frequency is limited to once every 5 minutes.

---

# 10. Batch data for one day

*Page ID: `11292916133591058`*

**Brief Description:**

- Retrieve all detailed data for a specific day from a list of devices based on their SNs, device type, and date. The data returned by the API will only include information for devices that the secret token has permission to access. Devices without permission will not have their data returned.
- `The device type is the deviceType parameter from the Get Device List API.`

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryDevicesHistoricalData`
  
**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description |
|:---------------|:---------|:-------|:------------|
| token          | Yes      | String | Secret token |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type   | Description |
|:---------------|:---------|:-------|:------------|
| deviceSn       | Yes      | String | Array of inverter serial numbers (SN), up to 50. Device serial numbers should be separated by commas. Example: xxxx,xxxxx,xxxx (maximum of 50) |
| deviceType     | Yes      | String | [Device Type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |
| date           | Yes      | String | Start date (format: yyyy-mm-dd). Example: 2024-05-14 |

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003,FDCJQ00002&quot;,
&quot;deviceType&quot;: &quot;min&quot;,
&quot;date&quot;: &quot;2024-05-14&quot;
}
```

**Return Example**

inv:   https://www.showdoc.com.cn/2540838290984246/11292917584269311
storage: https://www.showdoc.com.cn/2540838290984246/11292918959841019
sph:  https://www.showdoc.com.cn/2540838290984246/11292922712705121
max: https://www.showdoc.com.cn/2540838290984246/11292920771207078
spa: https://www.showdoc.com.cn/2540838290984246/11292925068299407
min: https://www.showdoc.com.cn/2540838290984246/11292926895869382
wit: https://www.showdoc.com.cn/2540838290984246/11292928841081078
sph-s: https://www.showdoc.com.cn/2540838290984246/11292930141133325
noah：https://www.showdoc.com.cn/2540838290984246/11315142054122408

**Remarks**

- The retrieval frequency is once every 5 minutes or less.

---

# 11. query high-frequency data

*Page ID: `11559060626625550`*

**Brief Description:**

- Query high-frequency data of a specific device based on its serial number and device type. This API only returns data for devices that the key token has permission to access. Devices without access permission will not be returned.
- `The device type corresponds to the deviceType parameter in the fetch device list interface.`

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryDfcData`
- Replace the prefix according to the domain name.

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description                  |
|:---------------|:---------|:-------|:-----------------------------|
| token          | Yes      | String | Secret token                 |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type   | Description                              |
|:---------------|:---------|:-------|:-----------------------------------------|
| deviceSn       | Yes      | String | Device unique serial number (SN)         |
| deviceType     | Yes      | String | [Device type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |

**Example Call**

```
{
  &quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
  &quot;deviceType&quot;: &quot;min&quot;
}
```

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;activePower&quot;: 0.00,
        &quot;batPower&quot;: -4816.00,
        &quot;batteryList&quot;: [
            {
                &quot;chargePower&quot;: 0.00,
                &quot;dischargePower&quot;: 2511.00,
                &quot;ibat&quot;: -6.40,
                &quot;index&quot;: 1,
                &quot;soc&quot;: 100,
                &quot;vbat&quot;: 376.50
            },
            {
                &quot;chargePower&quot;: 0.00,
                &quot;dischargePower&quot;: 2305.00,
                &quot;ibat&quot;: -6.10,
                &quot;index&quot;: 2,
                &quot;soc&quot;: 100,
                &quot;vbat&quot;: 375.80
            }
        ],
        &quot;batteryStatus&quot;: 3,
        &quot;pac&quot;: 4562.80,
        &quot;payLoadPower&quot;: 365.90,
        &quot;ppv&quot;: 0.00,
        &quot;priority&quot;: 2,
        &quot;reverActivePower&quot;: 4450.10,
        &quot;serialNum&quot;: &quot;DLP0DA7888&quot;,
        &quot;soc&quot;: 100,
        &quot;status&quot;: 6,
        &quot;utcTime&quot;: &quot;2026-02-25 00:10:01&quot;,
        &quot;vac1&quot;: 234.64,
        &quot;vac2&quot;: 235.04,
        &quot;vac3&quot;: 234.17
    }
}
```

**Return Parameter Description**

| Parameter Name | Type | Example | Description |
|------------|------|---------|-------------|
| code | int | 0 | API status code, 0 indicates success |
| data | object | - | Main data object |
| data.activePower | double | 0.0 | Grid import power (positive value), unit: W |
| data.pac | double | 2871.4 | AC output power, unit: W |
| data.ppv | double | 3045.3 | PV generation power, unit: W |
| data.payLoadPower | double | 258.4000000000001 | Total load power (calculated value), unit: W |
| data.reverActivePower | double | 2781.9 | Feed-in power, unit: W |
| data.batteryStatus | int | 3 | Overall battery status |
| data.batPower | double | 200.5 | Total battery charge/discharge power (positive = charging, negative = discharging, 0 = idle), unit: W |
| data.priority | int | 2 | Operating priority |
| data.serialNum | string | DLP0DA7888 | Device serial number |
| data.status | int | 6 | Device operating status code |
| data.utcTime | string | 2026-02-25 00:10:01 | Timestamp in UTC (offset +00:00), formatted as yyyy-MM-dd HH:mm:ss
 |
| data.vac1 | double | 234 | Phase voltage 1 |
| data.vac2 | double | 233 | Phase voltage 2 |
| data.vac3 | double | 234.5 | Phase voltage 3 |
| data.soc | int | 3 | Average battery SOC |
| data.batteryList | array | [...] | Battery information list |
| data.batteryList[].index | int | 1 | Battery index (starting from 1) |
| data.batteryList[].soc | int | 22 | Battery State of Charge (percentage) |
| data.batteryList[].chargePower | double | 5.0 | Battery charging power, unit: W |
| data.batteryList[].dischargePower | double | 0.0 | Battery discharging power, unit: W |
| data.batteryList[].ibat | double | 0.0 | Battery current (low-voltage side), unit: A |
| data.batteryList[].vbat | double | 370.6 | Battery voltage (low-voltage side), unit: V |


**Note: Status values defined in the param**


**status**

0: Standby
1: Self-check
3: Fault
4: Upgrade
5: PV online &amp; Battery offline &amp; Grid-connected
6: PV offline (or online) &amp; Battery online &amp; Grid-connected
7: PV online &amp; Battery online &amp; Off-grid
8: PV offline &amp; Battery online &amp; Off-grid
9: Bypass mode


**batteryStatus**

0: Battery standby
1: Battery disconnected
2: Battery charging
3: Battery discharging
4: Fault
5: Upgrade



**priority**

0: Load priority
1: Battery priority
2: Grid priority





---

# 12. Query partial additional device information

*Page ID: `11559060626973442`*

**Brief Description:**

- Query partial additional device information based on its serial number and device type. This API only returns data for devices that the key token has permission to access. Devices without access permission will not be returned.
- `The device type corresponds to the deviceType parameter in the fetch device list interface.`

**Request URL:**
- `https://openapi.growatt.com/v4/new-api/queryDeviceInfoParam`
- Replace the prefix according to the domain name.

**Request Method:**
- POST

**Content-Type:**
- application/x-www-form-urlencoded

**HTTP Header Parameters and Description:**

| Parameter Name | Required | Type   | Description                  |
|:---------------|:---------|:-------|:-----------------------------|
| token          | Yes      | String | Secret token                 |

**HTTP Body Parameters and Description:**

| Parameter Name | Required | Type   | Description                              |
|:---------------|:---------|:-------|:-----------------------------------------|
| deviceSn       | Yes      | String | Device unique serial number (SN)         |
| deviceType     | Yes      | String | [Device type](https://www.showdoc.com.cn/p/b42ee029e131c68c4dbfdd89285c0ec1 &quot;Device Type&quot;) |

**Example Call**

```
{
  &quot;deviceSn&quot;: &quot;SPA0B2300X&quot;,
  &quot;deviceType&quot;: &quot;min&quot;
}
```

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
	  &quot;deviceSn&quot;: &quot;SPA0B2300X&quot;,
	  &quot;deviceType&quot;: &quot;min&quot;,
	  &quot;deviceModel&quot;: &quot;XXX&quot;,
	  &quot;dataloggerModel&quot;: &quot;ShineWiFi-X&quot;,
	  &quot;batteryModel&quot;: &quot;XXXX&quot;,
	  &quot;norminalPower&quot;: 6000,
	  &quot;batteryCapacity&quot;: 6.5,
	  &quot;batteryNominalPower&quot;: 3000.0,
	  &quot;hasBattery&quot;: true
}

}
```

**Return Parameter Description**

| Parameter Name | Type | Example | Description |
|---|---|---|---|
| deviceSn | String | &quot;SPA0B2300X&quot; | Device serial number |
| deviceType | String | &quot;inv&quot; | Device type |
| deviceModel | String | &quot;SPH 6000TL3 BH-UP&quot; | Device model |
| dataloggerModel | String | &quot;ShineWiFi-X&quot; | Datalogger model |
| batteryModel | String | &quot;GBLI6532&quot; | Battery model |
| norminalPower | int | 6000 | Device nominal power (W) |
| batteryCapacity | double | 6.5 | Battery nominal capacity (kWh) |
| batteryNominalPower | double | 3000.0 | Battery nominal power (W) |
| hasBattery | boolean | true | Whether the device has a battery |





---

# 13. inv Basic Information

*Page ID: `11292916280672808`*

**Brief Description:**

- The data return format for the basic information of inv devices and the description of some parameters of the basic information.
- `Applicable only to: Batch retrieval of basic information of devices.`

 **Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;inv&quot;: [
            {
                &quot;id&quot;: 7,
                &quot;serialNum&quot;: &quot;HPB3744071&quot;,
                &quot;alias&quot;: &quot;HPB3744071&quot;,
                &quot;bigDevice&quot;: false,
                &quot;address&quot;: 1,
                &quot;location&quot;: &quot;在这&quot;,
                &quot;userID&quot;: 0,
                &quot;dataLogSn&quot;: &quot;JPC2101182&quot;,
                &quot;createDate&quot;: null,
                &quot;groupID&quot;: 0,
                &quot;nominalPower&quot;: 6000,
                &quot;power&quot;: 0.0,
                &quot;eToday&quot;: 0.0,
                &quot;eTotal&quot;: 0.0,
                &quot;lastUpdateTime&quot;: 1613805596000,
                &quot;fwVersion&quot;: &quot;AH1.0&quot;,
                &quot;innerVersion&quot;: &quot;ahbb1916&quot;,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;energyMonth&quot;: 0.0,
                &quot;lost&quot;: true,
                &quot;status&quot;: -1,
                &quot;tcpServerIp&quot;: &quot;192.168.3.35&quot;,
                &quot;updateExist&quot;: false,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;modelText&quot;: &quot;A1B0D1T0PFU1M7S1&quot;,
                &quot;communicationVersion&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;model&quot;: 269545841,
                &quot;rfStick&quot;: null,
                &quot;energyDayMap&quot;: {},
                &quot;temperature&quot;: 0.0,
                &quot;ipm_temperature&quot;: 0.0,
                &quot;deviceType&quot;: 0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;userName&quot;: null,
                &quot;optimezerList&quot;: null,
                &quot;invSetBean&quot;: null,
                &quot;level&quot;: 4,
                &quot;children&quot;: null,
                &quot;treeID&quot;: &quot;HPB3744071&quot;,
                &quot;treeName&quot;: &quot;HPB3744071&quot;,
                &quot;parentID&quot;: &quot;LIST_JPC2101182_0&quot;,
                &quot;loadText&quot;: &quot;0%&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;lastUpdateTimeText&quot;: &quot;2021-02-20 15:19:56&quot;,
                &quot;statusText&quot;: &quot;inverter.status.lost&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;,
                &quot;inverterInfoStatusCss&quot;: &quot;vsts_table_ash&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type   | Description |
|:---------------|:-------|-------------|
| serialNum      | string | Device SN   |
| dataloggerSn   | string | Data logger SN associated with the inverter |
| lost           | string | Device online status (0: online, 1: offline) |
| status         | int    | Device status (0: waiting, 1: normal, 3: fault) |
| alias          | int    | Alias       |
| location       | string | Address     |
| dataLogSn      | string | Associated data logger serial number |
| nominalPower   | string | Nominal power |
| lastUpdateTime | string | Last update time |
| tcpServerIp    | string | Server address |
| fwVersion      | string | Inverter version |

**Notes**

- The retrieval frequency is once every 5 minutes.
        

---

# 14. inv Last Detailed Data

*Page ID: `11292916843107127`*

  
**Brief Description:**

- Data format and parameter description of the last detailed data of the inv device
- `Only applicable to: Batch retrieval of the last data of devices.`

**Return Example**
``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;inv&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;serialNum&quot;: &quot;HTB1708008&quot;,
                &quot;time&quot;: &quot;2024-05-25 16:56:33&quot;,
                &quot;bigDevice&quot;: false,
                &quot;status&quot;: 1,
                &quot;vpv1&quot;: 741.3,
                &quot;ipv1&quot;: 1.5,
                &quot;ppv1&quot;: 1111.9,
                &quot;vpv2&quot;: 82.1,
                &quot;ipv2&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv&quot;: 1111.9,
                &quot;vacr&quot;: 481.6,
                &quot;vacs&quot;: 497.5,
                &quot;vact&quot;: 505.3,
                &quot;iacr&quot;: 1.0,
                &quot;iacs&quot;: 1.1,
                &quot;iact&quot;: 1.1,
                &quot;fac&quot;: 49.98,
                &quot;pac&quot;: 936.6,
                &quot;pacr&quot;: 277.4,
                &quot;pacs&quot;: 315.3,
                &quot;pact&quot;: 320.2,
                &quot;faultType&quot;: 0,
                &quot;temperature&quot;: 47.1,
                &quot;powerToday&quot;: 15.7,
                &quot;powerTotal&quot;: 130.3,
                &quot;timeTotal&quot;: 94.97958333333334,
                &quot;ipmTemperature&quot;: 40.7,
                &quot;pBusVoltage&quot;: 381.7,
                &quot;nBusVoltage&quot;: 382.2,
                &quot;pf&quot;: 1.0,
                &quot;epv1Today&quot;: 18.2,
                &quot;epv1Total&quot;: 139.3,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epvTotal&quot;: 139.3,
                &quot;rac&quot;: 0.0,
                &quot;eRacToday&quot;: 0.0,
                &quot;eRacTotal&quot;: 0.0,
                &quot;warnCode&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;warningValue2&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;strFault&quot;: 0,
                &quot;dwStringWarningValue1&quot;: 0,
                &quot;wStringStatusValue&quot;: 0,
                &quot;wPIDFaultValue&quot;: 0,
                &quot;vPidPvape&quot;: 0.0,
                &quot;iPidPvape&quot;: 0.0,
                &quot;pidStatus&quot;: 0,
                &quot;vPidPvbpe&quot;: 0.0,
                &quot;iPidPvbpe&quot;: 0.0,
                &quot;inverterBean&quot;: null,
                &quot;timeTotalText&quot;: &quot;95&quot;,
                &quot;timeCalendar&quot;: 1716627393328,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;warningValue1&quot;: 0
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name      | Type   | Description                                                                 |
|:--------------------|:-------|:---------------------------------------------------------------------------|
| serialNum          | string | Device SN.                                                                 |
| status              | string | Inverter status (0: Waiting, 1: Normal, 3: Fault).                         |
| ipv1                | string | Input current channel 1 (A).                                               |
| ipv2                | string | Input current channel 2 (A).                                               |
| ipv3                | string | Input current channel 3 (A).                                               |
| vpv1                | string | Input voltage channel 1 (V).                                               |
| vpv2                | string | Input voltage channel 2 (V).                                               |
| vpv3                | string | Input voltage channel 3 (V).                                               |
| ppv1                | string | Input power channel 1 (W).                                                 |
| ppv2                | string | Input power channel 2 (W).                                                 |
| ppv3                | string | Input power channel 3 (W).                                                 |
| iacr                | string | Output current channel 1 (A).                                              |
| iacs                | string | Output current channel 2 (A).                                              |
| iact                | string | Output current channel 3 (A).                                              |
| vacr                | string | Output voltage channel 1 (V).                                              |
| vacs                | string | Output voltage channel 2 (V).                                              |
| vact                | string | Output voltage channel 3 (V).                                              |
| pacr                | string | Output power channel 1 (W).                                                |
| pacs                | string | Output power channel 2 (W).                                                |
| pact                | string | Output power channel 3 (W).                                                |
| ppv                 | string | Input PV power (W).                                                        |
| pac                 | string | Output power (W).                                                          |
| powerToday          | string | Power generated today (kWh).                                               |
| powerTotal          | string | Total power generated (kWh).                                               |
| temperature         | string | Temperature (℃).                                                           |
| fac                 | string | Frequency (Hz).                                                            |
| pf                  | string | Power factor.                                                              |
| time                | string | Data time.                                                                 |
| faultType           | string | Fault code.                                                                |
| timeTotal           | string | Runtime.                                                                   |
| ipmTemperature      | string | IPM temperature.                                                           |
| epv1Today           | string | Input channel 1 power generated today (kWh).                               |
| epv1Total           | string | Input channel 1 total power generated (kWh).                               |
| epv2Today           | string | Input channel 2 power generated today (kWh).                               |
| epv2Total           | string | Input channel 2 total power generated (kWh).                               |
| epvTotal            | string | Total input power generated (kWh).                                         |
| eRacToday           | string | Reactive power generated today (kWh).                                      |
| eRacTotal           | string | Total reactive power generated (kWh).                                      |
| pBusVoltage         | string | P BUS voltage (V).                                                         |
| nBusVoltage         | string | N BUS voltage (V).                                                         |
| dwStringWarningValue1 | string | dwStringWarn warning.                                                     |
| wStringStatusValue  | string | wStringStatusValue error code.                                             |
| wPIDFaultValue      | string | wPIDFaultValue error code.                                                 |
| vPidPvape           | string | PID PVAPE voltage.                                                         |
| iPidPvape           | string | PID PVAPE current.                                                         |
| pidStatus           | string | PID status.                                                                |
| vPidPvbpe           | string | PID PVBPE voltage.                                                         |
| iPidPvbpe           | string | PID PVBPE current.                                                         |
| strFault            | string | PID strFault.                                                              |
| vString1            | string | Voltage of channel 1 (V).                                                  |
| vString2            | string | Voltage of channel 2 (V).                                                  |
| vString3            | string | Voltage of channel 3 (V).                                                  |
| vString4            | string | Voltage of channel 4 (V).                                                  |
| vString5            | string | Voltage of channel 5 (V).                                                  |
| vString6            | string | Voltage of channel 6 (V).                                                  |
| vString7            | string | Voltage of channel 7 (V).                                                  |
| vString8            | string | Voltage of channel 8 (V).                                                  |
| currentString1      | string | Current of channel 1 (A).                                                  |
| currentString2      | string | Current of channel 2 (A).                                                  |
| currentString3      | string | Current of channel 3 (A).                                                  |
| currentString4      | string | Current of channel 4 (A).                                                  |
| currentString5      | string | Current of channel 5 (A).                                                  |
| currentString6      | string | Current of channel 6 (A).                                                  |
| currentString7      | string | Current of channel 7 (A).                                                  |
| currentString8      | string | Current of channel 8 (A).                                                  |
| warnCode            | string | Warning code.                                                              |

**Remarks**

- The frequency of retrieval is once every 5 minutes.


---

# 15. inv Device Historical Data

*Page ID: `11292917584269311`*

**Brief Description:**

- Data format and parameter explanation for the historical data of inv devices
- `Only applicable to: Retrieve all detailed data of a specific device for a specific day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;datas&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;inverterId&quot;: &quot;HTB1708008&quot;,
                &quot;time&quot;: &quot;2024-05-25 16:56:33&quot;,
                &quot;bigDevice&quot;: false,
                &quot;status&quot;: 1,
                &quot;vpv1&quot;: 741.3,
                &quot;ipv1&quot;: 1.5,
                &quot;ppv1&quot;: 1111.9,
                &quot;vpv2&quot;: 82.1,
                &quot;ipv2&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv&quot;: 1111.9,
                &quot;vacr&quot;: 481.6,
                &quot;vacs&quot;: 497.5,
                &quot;vact&quot;: 505.3,
                &quot;iacr&quot;: 1.0,
                &quot;iacs&quot;: 1.1,
                &quot;iact&quot;: 1.1,
                &quot;fac&quot;: 49.98,
                &quot;pac&quot;: 936.6,
                &quot;pacr&quot;: 277.4,
                &quot;pacs&quot;: 315.3,
                &quot;pact&quot;: 320.2,
                &quot;faultType&quot;: 0,
                &quot;temperature&quot;: 47.1,
                &quot;powerToday&quot;: 0.0,
                &quot;powerTotal&quot;: 0.0,
                &quot;timeTotal&quot;: 94.97958333333334,
                &quot;ipmTemperature&quot;: 40.7,
                &quot;pBusVoltage&quot;: 381.7,
                &quot;nBusVoltage&quot;: 382.2,
                &quot;pf&quot;: 1.0,
                &quot;epv1Today&quot;: 18.2,
                &quot;epv1Total&quot;: 139.3,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epvTotal&quot;: 139.3,
                &quot;rac&quot;: 0.0,
                &quot;eRacToday&quot;: 0.0,
                &quot;eRacTotal&quot;: 0.0,
                &quot;warnCode&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;warningValue2&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;strFault&quot;: 0,
                &quot;dwStringWarningValue1&quot;: 0,
                &quot;wStringStatusValue&quot;: 0,
                &quot;wPIDFaultValue&quot;: 0,
                &quot;vPidPvape&quot;: 0.0,
                &quot;iPidPvape&quot;: 0.0,
                &quot;pidStatus&quot;: 0,
                &quot;vPidPvbpe&quot;: 0.0,
                &quot;iPidPvbpe&quot;: 0.0,
                &quot;inverterBean&quot;: null,
                &quot;timeTotalText&quot;: &quot;95&quot;,
                &quot;timeCalendar&quot;: 1716627393000,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;warningValue1&quot;: 0
            },
		],
		&quot;start&quot;: 1,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description** 

|Parameter Name|Type|Description|
|:-----  |:-----|----- |
| serialNum          | string | Device SN.                                                                 |
| status              | string | Inverter status (0: Waiting, 1: Normal, 3: Fault).                         |
| ipv1                | string | Input current channel 1 (A).                                               |
| ipv2                | string | Input current channel 2 (A).                                               |
| ipv3                | string | Input current channel 3 (A).                                               |
| vpv1                | string | Input voltage channel 1 (V).                                               |
| vpv2                | string | Input voltage channel 2 (V).                                               |
| vpv3                | string | Input voltage channel 3 (V).                                               |
| ppv1                | string | Input power channel 1 (W).                                                 |
| ppv2                | string | Input power channel 2 (W).                                                 |
| ppv3                | string | Input power channel 3 (W).                                                 |
| iacr                | string | Output current channel 1 (A).                                              |
| iacs                | string | Output current channel 2 (A).                                              |
| iact                | string | Output current channel 3 (A).                                              |
| vacr                | string | Output voltage channel 1 (V).                                              |
| vacs                | string | Output voltage channel 2 (V).                                              |
| vact                | string | Output voltage channel 3 (V).                                              |
| pacr                | string | Output power channel 1 (W).                                                |
| pacs                | string | Output power channel 2 (W).                                                |
| pact                | string | Output power channel 3 (W).                                                |
| ppv                 | string | Input PV power (W).                                                        |
| pac                 | string | Output power (W).                                                          |
| powerToday          | string | Power generated today (kWh).                                               |
| powerTotal          | string | Total power generated (kWh).                                               |
| temperature         | string | Temperature (℃).                                                           |
| fac                 | string | Frequency (Hz).                                                            |
| pf                  | string | Power factor.                                                              |
| time                | string | Data time.                                                                 |
| faultType           | string | Fault code.                                                                |
| timeTotal           | string | Runtime.                                                                   |
| ipmTemperature      | string | IPM temperature.                                                           |
| epv1Today           | string | Input channel 1 power generated today (kWh).                               |
| epv1Total           | string | Input channel 1 total power generated (kWh).                               |
| epv2Today           | string | Input channel 2 power generated today (kWh).                               |
| epv2Total           | string | Input channel 2 total power generated (kWh).                               |
| epvTotal            | string | Total input power generated (kWh).                                         |
| eRacToday           | string | Reactive power generated today (kWh).                                      |
| eRacTotal           | string | Total reactive power generated (kWh).                                      |
| pBusVoltage         | string | P BUS voltage (V).                                                         |
| nBusVoltage         | string | N BUS voltage (V).                                                         |
| dwStringWarningValue1 | string | dwStringWarn warning.                                                     |
| wStringStatusValue  | string | wStringStatusValue error code.                                             |
| wPIDFaultValue      | string | wPIDFaultValue error code.                                                 |
| vPidPvape           | string | PID PVAPE voltage.                                                         |
| iPidPvape           | string | PID PVAPE current.                                                         |
| pidStatus           | string | PID status.                                                                |
| vPidPvbpe           | string | PID PVBPE voltage.                                                         |
| iPidPvbpe           | string | PID PVBPE current.                                                         |
| strFault            | string | PID strFault.                                                              |
| vString1            | string | Voltage of channel 1 (V).                                                  |
| vString2            | string | Voltage of channel 2 (V).                                                  |
| vString3            | string | Voltage of channel 3 (V).                                                  |
| vString4            | string | Voltage of channel 4 (V).                                                  |
| vString5            | string | Voltage of channel 5 (V).                                                  |
| vString6            | string | Voltage of channel 6 (V).                                                  |
| vString7            | string | Voltage of channel 7 (V).                                                  |
| vString8            | string | Voltage of channel 8 (V).                                                  |
| currentString1      | string | Current of channel 1 (A).                                                  |
| currentString2      | string | Current of channel 2 (A).                                                  |
| currentString3      | string | Current of channel 3 (A).                                                  |
| currentString4      | string | Current of channel 4 (A).                                                  |
| currentString5      | string | Current of channel 5 (A).                                                  |
| currentString6      | string | Current of channel 6 (A).                                                  |
| currentString7      | string | Current of channel 7 (A).                                                  |
| currentString8      | string | Current of channel 8 (A).                                                  |
| warnCode            | string | Warning code.                                                              |


 **Remarks** 

- The retrieval frequency is once every 5 minutes



---

# 16. Storage Basic Information

*Page ID: `11292917862205677`*

**Brief Description:**

- The data return format for the basic information of storage devices and partial parameter descriptions of the basic information.
- `Only applicable to: Batch retrieval of basic device information.`


**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;storage&quot;: [
            {
                &quot;serialNum&quot;: &quot;JNK1CJM0GR&quot;,
                &quot;portName&quot;: null,
                &quot;dataLogSn&quot;: &quot;DDD0CGA0CF&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;裁床照明+插座+大空调&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;067.01/068.01&quot;,
                &quot;model&quot;: 0,
                &quot;innerVersion&quot;: &quot;null&quot;,
                &quot;lost&quot;: true,
                &quot;status&quot;: 5,
                &quot;tcpServerIp&quot;: &quot;47.119.28.147&quot;,
                &quot;lastUpdateTime&quot;: 1716979679000,
                &quot;statusLed1&quot;: false,
                &quot;statusLed2&quot;: false,
                &quot;statusLed3&quot;: false,
                &quot;statusLed4&quot;: false,
                &quot;statusLed5&quot;: false,
                &quot;statusLed6&quot;: false,
                &quot;deviceType&quot;: 3,
                &quot;batteryType&quot;: 0,
                &quot;outputConfig&quot;: 3,
                &quot;chargeConfig&quot;: 0,
                &quot;utiOutStart&quot;: 0,
                &quot;utiOutEnd&quot;: 0,
                &quot;utiChargeStart&quot;: 0,
                &quot;utiChargeEnd&quot;: 0,
                &quot;pvModel&quot;: 0,
                &quot;acInModel&quot;: 1,
                &quot;outputVoltType&quot;: 1,
                &quot;outputFreqType&quot;: 0,
                &quot;overLoadRestart&quot;: 1,
                &quot;overTempRestart&quot;: 1,
                &quot;buzzerEN&quot;: 1,
                &quot;maxChargeCurr&quot;: 1000,
                &quot;batLowToUtiVolt&quot;: 46.0,
                &quot;sysTime&quot;: &quot;2024-05-29 07:57&quot;,
                &quot;bulkChargeVolt&quot;: 56.4,
                &quot;floatChargeVolt&quot;: 54.0,
                &quot;rateWatt&quot;: 5000,
                &quot;rateVA&quot;: 5000,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;modelText&quot;: &quot;A0B0D0T0P0U0M0S0&quot;,
                &quot;powSavingEn&quot;: 0,
                &quot;uwBatType2&quot;: 0,
                &quot;bLightEn&quot;: 0,
                &quot;manualStartEn&quot;: 0,
                &quot;sciLossChkEn&quot;: 0,
                &quot;communicationVersion&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;userName&quot;: null,
                &quot;mainsToBatteryOperatPoint&quot;: 0.0,
                &quot;liBatteryProtocolType&quot;: 0,
                &quot;batteryUndervoltageCutoffPoint&quot;: 42.0,
                &quot;uwFeedEn&quot;: 0,
                &quot;uwLoadFirst&quot;: 0,
                &quot;uwFeedRange&quot;: 0,
                &quot;dtc&quot;: 20105,
                &quot;level&quot;: 4,
                &quot;children&quot;: null,
                &quot;statusText&quot;: &quot;inverter.status.lost&quot;,
                &quot;acmaxChargeCurr&quot;: 30,
                &quot;treeName&quot;: &quot;裁床照明+插座+大空调&quot;,
                &quot;treeID&quot;: &quot;ST_JNK1CJM0GR&quot;,
                &quot;parentID&quot;: &quot;LIST_DDD0CGA0CF_96&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-29 18:47:59&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description**

| Parameter Name | Type | Description |
|:-----  |:-----|----- |
| serialNum | string  | Device SN |
| dataloggerSn | string  | SN of the data logger associated with the energy storage device |
| lost | string  | Device online status (0: Online, 1: Offline) |
| status | int  | Device status, status (0: Offline, 1: Online, 2: Charging, 3: Discharging, 4: Error, 5: Burning, 6: Solar Charging, 7: Grid Charging, 8: Combined Charging (both solar and grid), 9: Combined Charging and Bypass (Grid) Output, 10: PV Charging and Bypass (Grid) Output, 11: Grid Charging and Bypass (Grid) Output, 12: Bypass (Grid) Output, 13: Solar Charging and Discharging Simultaneously, 14: Grid Charging and Discharging Simultaneously) (Shangk: 1: No Output, 2: Reserved, 3: Discharging, 4: Error, 5: Burning, 6: Solar Charging, 7: Grid Charging, 8: Combined Charging (both solar and grid), 9: Combined Charging and Bypass (Grid) Output, 10: PV Charging and Bypass (Grid) Output, 11: Grid Charging and Bypass (Grid) Output, 12: Bypass (Grid) Output, 13: Solar Charging and Discharging Simultaneously) |
| alias | string  | Alias |
| location | string  | Address |
| dataLogSn | string  | Serial number of the associated data logger |
| pCharge | string  | Charging power |
| pDischarge | string  | Discharging power |
| lastUpdateTime | string  | Last update time |
| tcpServerIp | string  | Server address |
| fwVersion | string  | Firmware version of the energy storage device |
| innerVersion | string  | Software version |

**Remarks**

- The retrieval frequency is once every 5 minutes.

---

# 17. The Last Detailed Data of Storage

*Page ID: `11292918042831939`*

  
**Brief Description:**

- Data format and parameter description of the last detailed data of the storage device
- `Only applicable for batch retrieval of the last data of the device.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;storage&quot;: [
            {
                &quot;serialNum&quot;: &quot;CDL0CJF08Z&quot;,
                &quot;dataLogSn&quot;: &quot;JVH0CJ5177&quot;,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716985060479,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 2,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;vpv&quot;: 0.0,
                &quot;ipv&quot;: 0.0,
                &quot;iCharge&quot;: 0.0,
                &quot;iDischarge&quot;: 0.0,
                &quot;ppv&quot;: 0.0,
                &quot;vBuck&quot;: 0.0,
                &quot;vac&quot;: 0.0,
                &quot;iacToUser&quot;: 0.0,
                &quot;pacToUser&quot;: 0.0,
                &quot;iacToGrid&quot;: 0.0,
                &quot;pacToGrid&quot;: 0.0,
                &quot;vBat&quot;: 52.89,
                &quot;capacity&quot;: 90,
                &quot;temperature&quot;: 0.0,
                &quot;ipmTemperature&quot;: 0.0,
                &quot;errorCode&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;dischargeToStandbyReason&quot;: 0,
                &quot;chargeToStandbyReason&quot;: 0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;gaugeBattteryStatus&quot;: 0,
                &quot;gaugeOperationStatus&quot;: 0,
                &quot;gaugePackStatus&quot;: 0,
                &quot;cycleCount&quot;: 0,
                &quot;maxChargeOrDischargeCurrent&quot;: 0,
                &quot;bmsCurrent&quot;: 0,
                &quot;bmsTemperature&quot;: 0,
                &quot;gaugeICCurrent&quot;: 0,
                &quot;gaugeRM1&quot;: 0,
                &quot;gaugeRM2&quot;: 0,
                &quot;vBus&quot;: 0.0,
                &quot;batTemp&quot;: 0.0,
                &quot;normalPower&quot;: 0,
                &quot;remoteCntlEn&quot;: 0,
                &quot;vpv2&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;pCharge2&quot;: 0.0,
                &quot;pDischarge2&quot;: 0.0,
                &quot;vBuck2&quot;: 0.0,
                &quot;epvToday2&quot;: 0.0,
                &quot;epvTotal2&quot;: 0.0,
                &quot;eChargeToday2&quot;: 0.0,
                &quot;eChargeTotal2&quot;: 0.0,
                &quot;eDischargeToday2&quot;: 0.0,
                &quot;eDischargeTotal2&quot;: 0.0,
                &quot;remoteCntlFailReason&quot;: 0,
                &quot;deviceType&quot;: 3,
                &quot;innerCWCode&quot;: null,
                &quot;constantVolt&quot;: 0,
                &quot;deltaVolt&quot;: 0,
                &quot;soh&quot;: 0,
                &quot;warnInfo&quot;: 0,
                &quot;cellVoltage1&quot;: 0,
                &quot;cellVoltage2&quot;: 0,
                &quot;cellVoltage3&quot;: 0,
                &quot;cellVoltage4&quot;: 0,
                &quot;cellVoltage5&quot;: 0,
                &quot;cellVoltage6&quot;: 0,
                &quot;cellVoltage7&quot;: 0,
                &quot;cellVoltage8&quot;: 0,
                &quot;cellVoltage9&quot;: 0,
                &quot;cellVoltage10&quot;: 0,
                &quot;cellVoltage11&quot;: 0,
                &quot;cellVoltage12&quot;: 0,
                &quot;cellVoltage13&quot;: 0,
                &quot;cellVoltage14&quot;: 0,
                &quot;cellVoltage15&quot;: 0,
                &quot;cellVoltage16&quot;: 0,
                &quot;bmsStatus2&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;constantVolt2&quot;: 0,
                &quot;deltaVolt2&quot;: 0,
                &quot;soh2&quot;: 0,
                &quot;cycleCount2&quot;: 0,
                &quot;maxChargeOrDischargeCurrent2&quot;: 0,
                &quot;bmsCurrent2&quot;: 0,
                &quot;bmsTemperature2&quot;: 0,
                &quot;warnInfo2&quot;: 0,
                &quot;gauge2RM1&quot;: 0,
                &quot;gauge2RM2&quot;: 0,
                &quot;cell2Voltage1&quot;: 0,
                &quot;cell2Voltage2&quot;: 0,
                &quot;cell2Voltage3&quot;: 0,
                &quot;cell2Voltage4&quot;: 0,
                &quot;cell2Voltage5&quot;: 0,
                &quot;cell2Voltage6&quot;: 0,
                &quot;cell2Voltage7&quot;: 0,
                &quot;cell2Voltage8&quot;: 0,
                &quot;cell2Voltage9&quot;: 0,
                &quot;cell2Voltage10&quot;: 0,
                &quot;cell2Voltage11&quot;: 0,
                &quot;cell2Voltage12&quot;: 0,
                &quot;cell2Voltage13&quot;: 0,
                &quot;cell2Voltage14&quot;: 0,
                &quot;cell2Voltage15&quot;: 0,
                &quot;cell2Voltage16&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0,
                &quot;bmsDeltaVolt&quot;: 0,
                &quot;bmsSoh&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsCellVoltage1&quot;: 0,
                &quot;bmsCellVoltage2&quot;: 0,
                &quot;bmsCellVoltage3&quot;: 0,
                &quot;bmsCellVoltage4&quot;: 0,
                &quot;bmsCellVoltage5&quot;: 0,
                &quot;bmsCellVoltage6&quot;: 0,
                &quot;bmsCellVoltage7&quot;: 0,
                &quot;bmsCellVoltage8&quot;: 0,
                &quot;bmsCellVoltage9&quot;: 0,
                &quot;bmsCellVoltage10&quot;: 0,
                &quot;bmsCellVoltage11&quot;: 0,
                &quot;bmsCellVoltage12&quot;: 0,
                &quot;bmsCellVoltage13&quot;: 0,
                &quot;bmsCellVoltage14&quot;: 0,
                &quot;bmsCellVoltage15&quot;: 0,
                &quot;bmsCellVoltage16&quot;: 0,
                &quot;dayMap&quot;: null,
                &quot;rateVA&quot;: 0,
                &quot;rateWatt&quot;: 0,
                &quot;chargeMonth&quot;: 0.0,
                &quot;dischargeMonth&quot;: 0.0,
                &quot;chgCurr&quot;: 0.0,
                &quot;dischgCurr&quot;: 10.1,
                &quot;eopDischrToday&quot;: 7.2,
                &quot;eopDischrTotal&quot;: 582.6,
                &quot;warnCode2&quot;: 0,
                &quot;bmsSoc&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsMaxCurrChg&quot;: 0.0,
                &quot;bmsCvolt&quot;: 0.0,
                &quot;bmsInfo&quot;: 0,
                &quot;bmsPackInfo&quot;: 0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCellVolt1&quot;: 0.0,
                &quot;bmsCellVolt2&quot;: 0.0,
                &quot;bmsCellVolt3&quot;: 0.0,
                &quot;bmsCellVolt4&quot;: 0.0,
                &quot;bmsCellVolt5&quot;: 0.0,
                &quot;bmsCellVolt6&quot;: 0.0,
                &quot;bmsCellVolt7&quot;: 0.0,
                &quot;bmsCellVolt8&quot;: 0.0,
                &quot;bmsCellVolt9&quot;: 0.0,
                &quot;bmsCellVolt10&quot;: 0.0,
                &quot;bmsCellVolt11&quot;: 0.0,
                &quot;bmsCellVolt12&quot;: 0.0,
                &quot;bmsCellVolt13&quot;: 0.0,
                &quot;bmsCellVolt14&quot;: 0.0,
                &quot;bmsCellVolt15&quot;: 0.0,
                &quot;bmsCellVolt16&quot;: 0.0,
                &quot;moduleId&quot;: 0,
                &quot;moduleTotalVolt&quot;: 0.0,
                &quot;moduleTotalCurr&quot;: 0.0,
                &quot;moduleSoc&quot;: 0,
                &quot;moduleStatus&quot;: 0,
                &quot;batProtect1&quot;: 0,
                &quot;batWarnInfo1&quot;: 0,
                &quot;packNum&quot;: 0,
                &quot;batDepowerReason&quot;: 0,
                &quot;gaugeRM&quot;: 0,
                &quot;gaugeFCC&quot;: 0,
                &quot;requestBatteryType&quot;: 0,
                &quot;maxCellVolt&quot;: 0.0,
                &quot;minCellVolt&quot;: 0.0,
                &quot;maxminCellVoltNum&quot;: 0,
                &quot;protectPackID&quot;: 0,
                &quot;manufacture&quot;: 0,
                &quot;hardwareVersion&quot;: 0,
                &quot;softwareVersion1&quot;: null,
                &quot;parallelHightSoftwarVer&quot;: 0,
                &quot;maxCellTemp&quot;: 0.0,
                &quot;minCellTemp&quot;: 0.0,
                &quot;maxminCellTempSerialNum&quot;: 0,
                &quot;maxminSoc&quot;: 0,
                &quot;totalCellNum&quot;: 0,
                &quot;batProtect2&quot;: 0,
                &quot;batProtect3&quot;: 0,
                &quot;batWarnInfo2&quot;: 0,
                &quot;updateStatus&quot;: 0,
                &quot;softwareVersion2&quot;: null,
                &quot;softwareVersion3&quot;: null,
                &quot;batSerialNumId&quot;: 0,
                &quot;batSerialNumber&quot;: null,
                &quot;moduleId2&quot;: 0,
                &quot;module2MaxVolt&quot;: 0.0,
                &quot;module2MinVolt&quot;: 0.0,
                &quot;module2MaxTemp&quot;: 0.0,
                &quot;module2MinTemp&quot;: 0.0,
                &quot;doStatus&quot;: 0,
                &quot;dsgBatNum&quot;: 0,
                &quot;dsgEnergy&quot;: 0,
                &quot;chgBatNum&quot;: 0,
                &quot;chgEnergy&quot;: 0,
                &quot;floatChargeVolt&quot;: 0.0,
                &quot;chargeMap&quot;: {},
                &quot;dischargeMap&quot;: {},
                &quot;faultCode&quot;: 0,
                &quot;epvToday&quot;: 12.9,
                &quot;epvTotal&quot;: 729.6,
                &quot;eChargeToday&quot;: 0.0,
                &quot;eChargeTotal&quot;: 0.0,
                &quot;eDischargeToday&quot;: 0.0,
                &quot;eDischargeTotal&quot;: 0.0,
                &quot;eToUserToday&quot;: 0.0,
                &quot;eToUserTotal&quot;: 0.0,
                &quot;eToGridToday&quot;: 250.5,
                &quot;eToGridTotal&quot;: 0.0,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;storageBean&quot;: null,
                &quot;chargeWay&quot;: 0,
                &quot;iChargePV1&quot;: 0.0,
                &quot;iChargePV2&quot;: 0.0,
                &quot;outPutPower&quot;: 498.0,
                &quot;pAcCharge&quot;: 0.0,
                &quot;vGrid&quot;: 228.7,
                &quot;freqGrid&quot;: 49.92,
                &quot;outPutVolt&quot;: 229.8,
                &quot;freqOutPut&quot;: 49.97,
                &quot;loadPercent&quot;: 12.5,
                &quot;outPutCurrent&quot;: 2.7,
                &quot;eacChargeToday&quot;: 0.0,
                &quot;eacChargeTotal&quot;: 227.3,
                &quot;eBatDisChargeToday&quot;: 2.1,
                &quot;eBatDisChargeTotal&quot;: 560.6,
                &quot;eacDisChargeToday&quot;: 0.0,
                &quot;eacDisChargeTotal&quot;: 474.1,
                &quot;iAcCharge&quot;: 0.0,
                &quot;pAcInPut&quot;: 0.0,
                &quot;pBat&quot;: 534.0,
                &quot;powSavingEn&quot;: 0,
                &quot;uwBatType2&quot;: 0,
                &quot;bLightEn&quot;: 0,
                &quot;manualStartEn&quot;: 0,
                &quot;sciLossChkEn&quot;: 0,
                &quot;time&quot;: &quot;2024-05-29 20:17:40&quot;,
                &quot;chargeMonthText&quot;: &quot;0&quot;,
                &quot;dischargeMapMap&quot;: {},
                &quot;dischargeMonthText&quot;: &quot;0&quot;,
                &quot;disChargeMonth&quot;: 0.0,
                &quot;spf5000StatusText&quot;: &quot;Battery Discharging&quot;,
                &quot;dischargeToStandbyReasonText&quot;: &quot;Unknown&quot;,
                &quot;chargeToStandbyReasonText&quot;: &quot;Unknown&quot;,
                &quot;pDischargeText&quot;: &quot;0.0 W&quot;,
                &quot;iDischargeText&quot;: &quot;0.0 A&quot;,
                &quot;eChargeTodayText&quot;: &quot;0.0 kWh&quot;,
                &quot;eChargeTotalText&quot;: &quot;0.0 kWh&quot;,
                &quot;eDischargeTodayText&quot;: &quot;0.0 kWh&quot;,
                &quot;eDischargeTotalText&quot;: &quot;0.0 kWh&quot;,
                &quot;sysOut&quot;: 0.0,
                &quot;capacityText&quot;: &quot;90 %&quot;,
                &quot;invTemperature&quot;: 28.1,
                &quot;dcDcTemperature&quot;: 26.6,
                &quot;buck1_NTCTemperature&quot;: 24.3,
                &quot;buck2_NTCTemperature&quot;: 28.2,
                &quot;statusText&quot;: &quot;Discharge&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;again&quot;: false,
                &quot;etotal&quot;: 729.6,
                &quot;etoday&quot;: 12.9,
                &quot;chargeDayMap&quot;: {},
                &quot;pChargeText&quot;: &quot;0.0 W&quot;,
                &quot;vpvText&quot;: &quot;0.0 V&quot;,
                &quot;ipvText&quot;: &quot;0.0 A&quot;,
                &quot;iChargeText&quot;: &quot;0.0 A&quot;,
                &quot;vBuckText&quot;: &quot;0.0 V&quot;,
                &quot;vBatText&quot;: &quot;52.89 V&quot;,
                &quot;vacText&quot;: &quot;0.0 V&quot;,
                &quot;iacToUserText&quot;: &quot;0.0 A&quot;,
                &quot;pacToUserText&quot;: &quot;0.0 W&quot;,
                &quot;iacToGridText&quot;: &quot;0.0 A&quot;,
                &quot;pacToGridText&quot;: &quot;0.0 W&quot;,
                &quot;ppvText&quot;: &quot;0.0 W&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description**

| Parameter Name | Type | Description |
|:-----  |:-----|----- |
| serialNum | string  | Storage device SN
| status | string  | Storage device status (0: Operating, 1: Charge, 2: Discharge, 3: Fault, 4: Flash)
| deviceType | string  | Storage device type (0: SP2000, 1: SP3000)
| pCharge | string  | Charging power (W)
| pDischarge | string  | Discharging power (W)
| vpv | string  | Input PV voltage (V)
| ipv | string  | Input PV current (A)
| iCharge | string  | PV end charging current (A)
| iDischarge | string  | PV end discharging current (A)
| ppv | string  | Panel input power (W)
| vBuck | string  | vBuk (A)
| vac | string  | Grid voltage (V)
| iacToUser | string  | User-side current (A)
| pacToUser | string  | User-side power (V)
| iacToGrid | string  | Grid-side current (A)
| pacToGrid | string  | Grid-side power (W)
| vBat | string  | Battery voltage (V)
| capacity | string  | Battery capacity (percentage)
| ipmTemperature | string  | IPM temperature (℃)
| epvToday | string  | Today's panel energy (kWh)
| epvTotal | string  | Total panel energy (kWh)
| temperature | string  | Temperature (℃)
| eChargeToday | string  | Today's charging energy (kWh)
| eChargeTotal | string  | Total charging energy (kWh)
| time | string  | Data time
| eDischargeToday | string  | Today's discharging energy (kWh)
| eDischargeTotal | string  | Total discharging energy (kWh)
| eToUserToday | string  | Today's energy (grid-to-user) (kWh)
| eToUserTotal | string  | Total energy (grid-to-user) (kWh)
| eToGridToday | string  | Today's energy (user-to-grid) (kWh)
| eToGridTotal | string  | Total energy (user-to-grid) (kWh)
| faultCode | string  | Fault code
| vpv2 | string  | SP3000 input PV voltage (V)
| ppv2 | string  | SP3000 panel input power (W)
| ipv2 | string  | SP3000 charging power (W)
| pDischarge2 | string  | SP3000 discharging power (W)
| vBuck2 | string  | vBuck2 (A)
| epvToday2 | string  | SP3000 today's panel energy (kWh)
| epvTotal2 | string  | SP3000 total panel energy (kWh)
| eChargeToday2 | string  | SP3000 today's charging energy (kWh)
| eChargeTotal2 | string  | SP3000 total charging energy (kWh)
| eDischargeToday2 | string  | SP3000 today's discharging energy (kWh)
| eDischargeTotal2 | string  | SP3000 total discharging energy (kWh)
| normalPower | string  | Current power (W)
| errorCode | string  | Error code
| warnCode | string  | Warning code
| iChargePV1 | string  | PV1 charging current
| iChargePV2 | string  | PV2 charging current
| outPutPower | string  | Output power
| pAcCharge | string  | AC charging power
| vGrid | string  | Grid voltage
| freqGrid | string  | Grid frequency
| outPutVolt | string  | Output voltage
| freqOutPut | string  | Output frequency
| loadPercent | string  | Load percentage
| outPutCurrent | string  | Output current
| eacChargeToday | string  | Today's AC charging energy
| eacChargeTotal | string  | Total AC charging energy
| eBatDisChargeToday | string  | Today's battery discharging energy
| eBatDisChargeTotal | string  | Total battery discharging energy
| eacDisChargeToday | string  | Today's AC bypass load energy
| eacDisChargeTotal | string  | Total AC bypass load energy
| iAcCharge | string  | AC charging current
| pAcInPut | string  | AC input energy
| InvTemperature | float  | InvTemp
| DcDcTemperature | float  | DcDc Temp
| Buck1_NTCTemperature | float  | Buck1 Temperature
| Buck2_NTCTemperature | float  | Buck2 Temperature

 **Remarks** 
- The retrieval frequency is once every 5 minutes.

---

# 18. Historical Data of Storage Devices

*Page ID: `11292918959841019`*

**Brief Description:**

- Data format and parameter description of historical data for storage devices
- `Only applicable for: Retrieving all detailed data for a specific device on a particular day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;JNK1CJM0GR&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716891880000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 5,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;vpv&quot;: 238.9,
                &quot;ipv&quot;: 0.0,
                &quot;iCharge&quot;: 0.0,
                &quot;iDischarge&quot;: 0.0,
                &quot;ppv&quot;: 3.0,
                &quot;vBuck&quot;: 0.0,
                &quot;vac&quot;: 0.0,
                &quot;iacToUser&quot;: 0.0,
                &quot;pacToUser&quot;: 0.0,
                &quot;iacToGrid&quot;: 0.0,
                &quot;pacToGrid&quot;: 0.0,
                &quot;vBat&quot;: 0.0,
                &quot;capacity&quot;: 0,
                &quot;temperature&quot;: 0.0,
                &quot;ipmTemperature&quot;: 0.0,
                &quot;errorCode&quot;: 0,
                &quot;warnCode&quot;: 40960,
                &quot;dischargeToStandbyReason&quot;: 0,
                &quot;chargeToStandbyReason&quot;: 0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;gaugeBattteryStatus&quot;: 0,
                &quot;gaugeOperationStatus&quot;: 0,
                &quot;gaugePackStatus&quot;: 0,
                &quot;cycleCount&quot;: 0,
                &quot;maxChargeOrDischargeCurrent&quot;: 0,
                &quot;bmsCurrent&quot;: 0,
                &quot;bmsTemperature&quot;: 0,
                &quot;gaugeICCurrent&quot;: 0,
                &quot;gaugeRM1&quot;: 0,
                &quot;gaugeRM2&quot;: 0,
                &quot;vBus&quot;: 0.0,
                &quot;batTemp&quot;: 0.0,
                &quot;normalPower&quot;: 0,
                &quot;remoteCntlEn&quot;: 0,
                &quot;vpv2&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;pCharge2&quot;: 0.0,
                &quot;pDischarge2&quot;: 0.0,
                &quot;vBuck2&quot;: 0.0,
                &quot;epvToday2&quot;: 0.0,
                &quot;epvTotal2&quot;: 0.0,
                &quot;eChargeToday2&quot;: 0.0,
                &quot;eChargeTotal2&quot;: 0.0,
                &quot;eDischargeToday2&quot;: 0.0,
                &quot;eDischargeTotal2&quot;: 0.0,
                &quot;remoteCntlFailReason&quot;: 0,
                &quot;deviceType&quot;: 3,
                &quot;innerCWCode&quot;: &quot;null&quot;,
                &quot;constantVolt&quot;: 0,
                &quot;deltaVolt&quot;: 0,
                &quot;soh&quot;: 0,
                &quot;warnInfo&quot;: 0,
                &quot;cellVoltage1&quot;: 0,
                &quot;cellVoltage2&quot;: 0,
                &quot;cellVoltage3&quot;: 0,
                &quot;cellVoltage4&quot;: 0,
                &quot;cellVoltage5&quot;: 0,
                &quot;cellVoltage6&quot;: 0,
                &quot;cellVoltage7&quot;: 0,
                &quot;cellVoltage8&quot;: 0,
                &quot;cellVoltage9&quot;: 0,
                &quot;cellVoltage10&quot;: 0,
                &quot;cellVoltage11&quot;: 0,
                &quot;cellVoltage12&quot;: 0,
                &quot;cellVoltage13&quot;: 0,
                &quot;cellVoltage14&quot;: 0,
                &quot;cellVoltage15&quot;: 0,
                &quot;cellVoltage16&quot;: 0,
                &quot;bmsStatus2&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;constantVolt2&quot;: 0,
                &quot;deltaVolt2&quot;: 0,
                &quot;soh2&quot;: 0,
                &quot;cycleCount2&quot;: 0,
                &quot;maxChargeOrDischargeCurrent2&quot;: 0,
                &quot;bmsCurrent2&quot;: 0,
                &quot;bmsTemperature2&quot;: 0,
                &quot;warnInfo2&quot;: 0,
                &quot;gauge2RM1&quot;: 0,
                &quot;gauge2RM2&quot;: 0,
                &quot;cell2Voltage1&quot;: 0,
                &quot;cell2Voltage2&quot;: 0,
                &quot;cell2Voltage3&quot;: 0,
                &quot;cell2Voltage4&quot;: 0,
                &quot;cell2Voltage5&quot;: 0,
                &quot;cell2Voltage6&quot;: 0,
                &quot;cell2Voltage7&quot;: 0,
                &quot;cell2Voltage8&quot;: 0,
                &quot;cell2Voltage9&quot;: 0,
                &quot;cell2Voltage10&quot;: 0,
                &quot;cell2Voltage11&quot;: 0,
                &quot;cell2Voltage12&quot;: 0,
                &quot;cell2Voltage13&quot;: 0,
                &quot;cell2Voltage14&quot;: 0,
                &quot;cell2Voltage15&quot;: 0,
                &quot;cell2Voltage16&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0,
                &quot;bmsDeltaVolt&quot;: 0,
                &quot;bmsSoh&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsCellVoltage1&quot;: 0,
                &quot;bmsCellVoltage2&quot;: 0,
                &quot;bmsCellVoltage3&quot;: 0,
                &quot;bmsCellVoltage4&quot;: 0,
                &quot;bmsCellVoltage5&quot;: 0,
                &quot;bmsCellVoltage6&quot;: 0,
                &quot;bmsCellVoltage7&quot;: 0,
                &quot;bmsCellVoltage8&quot;: 0,
                &quot;bmsCellVoltage9&quot;: 0,
                &quot;bmsCellVoltage10&quot;: 0,
                &quot;bmsCellVoltage11&quot;: 0,
                &quot;bmsCellVoltage12&quot;: 0,
                &quot;bmsCellVoltage13&quot;: 0,
                &quot;bmsCellVoltage14&quot;: 0,
                &quot;bmsCellVoltage15&quot;: 0,
                &quot;bmsCellVoltage16&quot;: 0,
                &quot;dayMap&quot;: null,
                &quot;rateVA&quot;: 0,
                &quot;rateWatt&quot;: 0,
                &quot;chargeMonth&quot;: 0.0,
                &quot;dischargeMonth&quot;: 0.0,
                &quot;chgCurr&quot;: 0.0,
                &quot;dischgCurr&quot;: 0.0,
                &quot;eopDischrToday&quot;: 30.7,
                &quot;eopDischrTotal&quot;: 30.7,
                &quot;warnCode2&quot;: 0,
                &quot;bmsSoc&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsMaxCurrChg&quot;: 0.0,
                &quot;bmsCvolt&quot;: 0.0,
                &quot;bmsInfo&quot;: 0,
                &quot;bmsPackInfo&quot;: 0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCellVolt1&quot;: 0.0,
                &quot;bmsCellVolt2&quot;: 0.0,
                &quot;bmsCellVolt3&quot;: 0.0,
                &quot;bmsCellVolt4&quot;: 0.0,
                &quot;bmsCellVolt5&quot;: 0.0,
                &quot;bmsCellVolt6&quot;: 0.0,
                &quot;bmsCellVolt7&quot;: 0.0,
                &quot;bmsCellVolt8&quot;: 0.0,
                &quot;bmsCellVolt9&quot;: 0.0,
                &quot;bmsCellVolt10&quot;: 0.0,
                &quot;bmsCellVolt11&quot;: 0.0,
                &quot;bmsCellVolt12&quot;: 0.0,
                &quot;bmsCellVolt13&quot;: 0.0,
                &quot;bmsCellVolt14&quot;: 0.0,
                &quot;bmsCellVolt15&quot;: 0.0,
                &quot;bmsCellVolt16&quot;: 0.0,
                &quot;moduleId&quot;: 0,
                &quot;moduleTotalVolt&quot;: 0.0,
                &quot;moduleTotalCurr&quot;: 0.0,
                &quot;moduleSoc&quot;: 0,
                &quot;moduleStatus&quot;: 0,
                &quot;batProtect1&quot;: 0,
                &quot;batWarnInfo1&quot;: 0,
                &quot;packNum&quot;: 0,
                &quot;batDepowerReason&quot;: 0,
                &quot;gaugeRM&quot;: 0,
                &quot;gaugeFCC&quot;: 0,
                &quot;requestBatteryType&quot;: 0,
                &quot;maxCellVolt&quot;: 0.0,
                &quot;minCellVolt&quot;: 0.0,
                &quot;maxminCellVoltNum&quot;: 0,
                &quot;protectPackID&quot;: 0,
                &quot;manufacture&quot;: 0,
                &quot;hardwareVersion&quot;: 0,
                &quot;softwareVersion1&quot;: null,
                &quot;parallelHightSoftwarVer&quot;: 0,
                &quot;maxCellTemp&quot;: 0.0,
                &quot;minCellTemp&quot;: 0.0,
                &quot;maxminCellTempSerialNum&quot;: 0,
                &quot;maxminSoc&quot;: 0,
                &quot;totalCellNum&quot;: 0,
                &quot;batProtect2&quot;: 0,
                &quot;batProtect3&quot;: 0,
                &quot;batWarnInfo2&quot;: 0,
                &quot;updateStatus&quot;: 0,
                &quot;softwareVersion2&quot;: null,
                &quot;softwareVersion3&quot;: null,
                &quot;batSerialNumId&quot;: 0,
                &quot;batSerialNumber&quot;: null,
                &quot;moduleId2&quot;: 0,
                &quot;module2MaxVolt&quot;: 0.0,
                &quot;module2MinVolt&quot;: 0.0,
                &quot;module2MaxTemp&quot;: 0.0,
                &quot;module2MinTemp&quot;: 0.0,
                &quot;doStatus&quot;: 0,
                &quot;dsgBatNum&quot;: 0,
                &quot;dsgEnergy&quot;: 0,
                &quot;chgBatNum&quot;: 0,
                &quot;chgEnergy&quot;: 0,
                &quot;floatChargeVolt&quot;: 0.0,
                &quot;chargeMap&quot;: {},
                &quot;dischargeMap&quot;: {},
                &quot;faultCode&quot;: 0,
                &quot;epvToday&quot;: 11.6,
                &quot;epvTotal&quot;: 3543.4,
                &quot;eChargeToday&quot;: 0.0,
                &quot;eChargeTotal&quot;: 0.0,
                &quot;eDischargeToday&quot;: 0.0,
                &quot;eDischargeTotal&quot;: 0.0,
                &quot;eToUserToday&quot;: 0.0,
                &quot;eToUserTotal&quot;: 0.0,
                &quot;eToGridToday&quot;: 236.7,
                &quot;eToGridTotal&quot;: 0.0,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;storageBean&quot;: null,
                &quot;chargeWay&quot;: 0,
                &quot;iChargePV1&quot;: 5.3,
                &quot;iChargePV2&quot;: 0.0,
                &quot;outPutPower&quot;: 0.0,
                &quot;pAcCharge&quot;: 0.0,
                &quot;vGrid&quot;: 0.0,
                &quot;freqGrid&quot;: 0.0,
                &quot;outPutVolt&quot;: 0.0,
                &quot;freqOutPut&quot;: 0.0,
                &quot;loadPercent&quot;: 0.0,
                &quot;outPutCurrent&quot;: 0.1,
                &quot;eacChargeToday&quot;: 0.0,
                &quot;eacChargeTotal&quot;: 0.0,
                &quot;eBatDisChargeToday&quot;: 0.0,
                &quot;eBatDisChargeTotal&quot;: 0.0,
                &quot;eacDisChargeToday&quot;: 30.7,
                &quot;eacDisChargeTotal&quot;: 6645.5,
                &quot;iAcCharge&quot;: 0.0,
                &quot;pAcInPut&quot;: 0.0,
                &quot;pBat&quot;: 0.0,
                &quot;powSavingEn&quot;: 0,
                &quot;uwBatType2&quot;: 0,
                &quot;bLightEn&quot;: 0,
                &quot;manualStartEn&quot;: 0,
                &quot;sciLossChkEn&quot;: 0,
                &quot;time&quot;: &quot;2024-05-28 18:24:40&quot;,
                &quot;chargeMonthText&quot;: &quot;0&quot;,
                &quot;dischargeMapMap&quot;: {},
                &quot;dischargeMonthText&quot;: &quot;0&quot;,
                &quot;disChargeMonth&quot;: 0.0,
                &quot;spf5000StatusText&quot;: &quot;PV Charging&quot;,
                &quot;dischargeToStandbyReasonText&quot;: &quot;Unknown&quot;,
                &quot;chargeToStandbyReasonText&quot;: &quot;Unknown&quot;,
                &quot;pDischargeText&quot;: &quot;0.0 W&quot;,
                &quot;iDischargeText&quot;: &quot;0.0 A&quot;,
                &quot;eChargeTodayText&quot;: &quot;0.0 kWh&quot;,
                &quot;eChargeTotalText&quot;: &quot;0.0 kWh&quot;,
                &quot;eDischargeTodayText&quot;: &quot;0.0 kWh&quot;,
                &quot;eDischargeTotalText&quot;: &quot;0.0 kWh&quot;,
                &quot;sysOut&quot;: 3.0,
                &quot;capacityText&quot;: &quot;0 %&quot;,
                &quot;invTemperature&quot;: 33.6,
                &quot;dcDcTemperature&quot;: 32.4,
                &quot;buck1_NTCTemperature&quot;: 31.5,
                &quot;buck2_NTCTemperature&quot;: 30.8,
                &quot;statusText&quot;: &quot;PV charge&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;again&quot;: false,
                &quot;etotal&quot;: 3543.4,
                &quot;etoday&quot;: 11.6,
                &quot;chargeDayMap&quot;: {},
                &quot;pChargeText&quot;: &quot;0.0 W&quot;,
                &quot;vpvText&quot;: &quot;238.9 V&quot;,
                &quot;ipvText&quot;: &quot;0.0 A&quot;,
                &quot;iChargeText&quot;: &quot;0.0 A&quot;,
                &quot;vBuckText&quot;: &quot;0.0 V&quot;,
                &quot;vBatText&quot;: &quot;0.0 V&quot;,
                &quot;vacText&quot;: &quot;0.0 V&quot;,
                &quot;iacToUserText&quot;: &quot;0.0 A&quot;,
                &quot;pacToUserText&quot;: &quot;0.0 W&quot;,
                &quot;iacToGridText&quot;: &quot;0.0 A&quot;,
                &quot;pacToGridText&quot;: &quot;0.0 W&quot;,
                &quot;ppvText&quot;: &quot;3.0 W&quot;
            },
			 ],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name         | Type   | Description                                                                               |
|:-----------------------|:-------|:-----------------------------------------------------------------------------------------|
| serialNum             | string | Storage device SN                                                                         |
| status                 | string | Storage device status (0: Operating, 1: Charge, 2: Discharge, 3: Fault, 4: Flash)         |
| deviceType             | string | Storage device type (0: SP2000, 1: SP3000)                                                |
| pCharge                | string | Charging power (W)                                                                        |
| pDischarge             | string | Discharging power (W)                                                                     |
| vpv                    | string | Input PV voltage (V)                                                                      |
| ipv                    | string | Input PV current (A)                                                                      |
| iCharge                | string | PV-end charging current (A)                                                               |
| iDischarge             | string | PV-end discharging current (A)                                                            |
| ppv                    | string | Panel input power (W)                                                                     |
| vBuck                  | string | vBuck (A)                                                                                 |
| vac                    | string | Grid voltage (V)                                                                          |
| iacToUser              | string | User-side current (A)                                                                     |
| pacToUser              | string | User-side power (W)                                                                       |
| iacToGrid              | string | Grid-side current (A)                                                                     |
| pacToGrid              | string | Grid-side power (W)                                                                       |
| vBat                   | string | Battery voltage (V)                                                                       |
| capacity               | string | Battery capacity (percentage)                                                             |
| ipmTemperature         | string | IPM temperature (℃)                                                                       |
| epvToday               | string | Today's panel energy (kWh)                                                                |
| epvTotal               | string | Total panel energy (kWh)                                                                  |
| temperature            | string | Temperature (℃)                                                                           |
| eChargeToday           | string | Today's charging energy (kWh)                                                             |
| eChargeTotal           | string | Total charging energy (kWh)                                                               |
| time                   | string | Data timestamp                                                                            |
| eDischargeToday        | string | Today's discharging energy (kWh)                                                          |
| eDischargeTotal        | string | Total discharging energy (kWh)                                                            |
| eToUserToday           | string | Today's energy from grid to user (kWh)                                                    |
| eToUserTotal           | string | Total energy from grid to user (kWh)                                                      |
| eToGridToday           | string | Today's energy from user to grid (kWh)                                                    |
| eToGridTotal           | string | Total energy from user to grid (kWh)                                                      |
| faultCode              | string | Fault code                                                                                |
| vpv2                   | string | SP3000 input PV voltage (V)                                                               |
| ppv2                   | string | SP3000 panel input power (W)                                                              |
| ipv2                   | string | SP3000 charging power (W)                                                                 |
| pDischarge2            | string | SP3000 discharging power (W)                                                              |
| vBuck2                 | string | vBuck2 (A)                                                                                |
| epvToday2              | string | SP3000 today's panel energy (kWh)                                                         |
| epvTotal2              | string | SP3000 total panel energy (kWh)                                                           |
| eChargeToday2          | string | SP3000 today's charging energy (kWh)                                                      |
| eChargeTotal2          | string | SP3000 total charging energy (kWh)                                                        |
| eDischargeToday2       | string | SP3000 today's discharging energy (kWh)                                                   |
| eDischargeTotal2       | string | SP3000 total discharging energy (kWh)                                                     |
| normalPower            | string | Current power (W)                                                                         |
| errorCode              | string | Error code                                                                                |
| warnCode               | string | Warning code                                                                              |
| iChargePV1             | string | PV1 charging current                                                                      |
| iChargePV2             | string | PV2 charging current                                                                      |
| outPutPower            | string | Output power                                                                              |
| pAcCharge              | string | AC charging power                                                                         |
| vGrid                  | string | Grid voltage                                                                              |
| freqGrid               | string | Grid frequency                                                                            |
| outPutVolt             | string | Output voltage                                                                            |
| freqOutPut             | string | Output frequency                                                                          |
| loadPercent            | string | Load percentage                                                                           |
| outPutCurrent          | string | Output current                                                                            |
| eacChargeToday         | string | AC today’s charging energy                                                                |
| eacChargeTotal         | string | AC total charging energy                                                                  |
| eBatDisChargeToday     | string | Battery today’s discharging energy                                                        |
| eBatDisChargeTotal     | string | Battery total discharging energy                                                          |
| eacDisChargeToday      | string | Grid today’s bypass load energy                                                           |
| eacDisChargeTotal      | string | Grid total bypass load energy                                                             |
| iAcCharge              | string | AC charging current                                                                       |
| pAcInPut               | string | AC input energy                                                                           |
| pBat                   | string | Battery power                                                                             |
| InvTemperature         | float  | InvTemp                                                                                   |
| DcDcTemperature        | float  | DcDc Temp                                                                                 |
| Buck1_NTCTemperature    | float  | Buck1 Temperature                                                                         |
| Buck2_NTCTemperature    | float  | Buck2 Temperature                                                                         |

**Remarks**

- The retrieval frequency is once every 5 minutes.

---

# 19. sph Basic Information

*Page ID: `11292921698309783`*

**Brief Description:**

- Data return format of basic information of SPH equipment and description of some parameters of basic information
- `Only applicable to: bulk retrieval of basic equipment information.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;sph&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;serialNum&quot;: &quot;OZD0849010&quot;,
                &quot;portName&quot;: &quot;ShinePano - JAD084800B&quot;,
                &quot;dataLogSn&quot;: &quot;JAD084800B&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;OZD0849010&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;RA1.0&quot;,
                &quot;model&quot;: 1159635200000,
                &quot;innerVersion&quot;: &quot;raab010101&quot;,
                &quot;lost&quot;: false,
                &quot;status&quot;: 5,
                &quot;tcpServerIp&quot;: &quot;47.119.173.58&quot;,
                &quot;lastUpdateTime&quot;: 1716535653000,
                &quot;sysTime&quot;: &quot;2024-05-24 05:20:52&quot;,
                &quot;deviceType&quot;: 0,
                &quot;communicationVersion&quot;: &quot;&quot;,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;energyMonth&quot;: 0.0,
                &quot;energyDayMap&quot;: {},
                &quot;onOff&quot;: 0,
                &quot;pmax&quot;: 0,
                &quot;vnormal&quot;: 360.0,
                &quot;lcdLanguage&quot;: 1,
                &quot;countrySelected&quot;: 0,
                &quot;wselectBaudrate&quot;: 0,
                &quot;comAddress&quot;: 1,
                &quot;manufacturer&quot;: &quot;   New Energy   &quot;,
                &quot;dtc&quot;: 3501,
                &quot;modbusVersion&quot;: 305,
                &quot;floatChargeCurrentLimit&quot;: 660.0,
                &quot;vbatWarning&quot;: 440.0,
                &quot;vbatWarnClr&quot;: 5.0,
                &quot;vbatStopForDischarge&quot;: 4.7,
                &quot;vbatStopForCharge&quot;: 5.75,
                &quot;vbatStartForDischarge&quot;: 44.0,
                &quot;vbatStartforCharge&quot;: 54.4,
                &quot;batTempLowerLimitD&quot;: 110.0,
                &quot;batTempUpperLimitD&quot;: 70.0,
                &quot;batTempLowerLimitC&quot;: 110.0,
                &quot;batTempUpperLimitC&quot;: 60.0,
                &quot;forcedDischargeTimeStart1&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart2&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart3&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop1&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop2&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop3&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart1&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart2&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart3&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop1&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop2&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop3&quot;: &quot;0:0&quot;,
                &quot;bctMode&quot;: 0,
                &quot;bctAdjust&quot;: 0,
                &quot;wdisChargeSOCLowLimit1&quot;: 100,
                &quot;wdisChargeSOCLowLimit2&quot;: 5,
                &quot;wchargeSOCLowLimit1&quot;: 100,
                &quot;wchargeSOCLowLimit2&quot;: 100,
                &quot;acChargeEnable&quot;: 0,
                &quot;priorityChoose&quot;: 1,
                &quot;chargePowerCommand&quot;: 100,
                &quot;disChargePowerCommand&quot;: 100,
                &quot;bagingTestStep&quot;: 0,
                &quot;batteryType&quot;: 0,
                &quot;epsFunEn&quot;: 1,
                &quot;epsVoltSet&quot;: 0,
                &quot;epsFreqSet&quot;: 0,
                &quot;forcedDischargeStopSwitch1&quot;: 0,
                &quot;forcedDischargeStopSwitch2&quot;: 0,
                &quot;forcedDischargeStopSwitch3&quot;: 0,
                &quot;forcedChargeStopSwitch1&quot;: 1,
                &quot;forcedChargeStopSwitch2&quot;: 0,
                &quot;forcedChargeStopSwitch3&quot;: 0,
                &quot;voltageHighLimit&quot;: 263.0,
                &quot;voltageLowLimit&quot;: 186.0,
                &quot;buckUpsFunEn&quot;: 0,
                &quot;uspFreqSet&quot;: 0,
                &quot;buckUPSVoltSet&quot;: 0,
                &quot;pvPfCmdMemoryState&quot;: 0,
                &quot;activeRate&quot;: 100,
                &quot;reactiveRate&quot;: 100,
                &quot;underExcited&quot;: 0,
                &quot;exportLimit&quot;: 0,
                &quot;exportLimitPowerRate&quot;: 0.0,
                &quot;powerFactor&quot;: 0.0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;chargeTime1&quot;: null,
                &quot;chargeTime2&quot;: null,
                &quot;chargeTime3&quot;: null,
                &quot;dischargeTime1&quot;: null,
                &quot;dischargeTime2&quot;: null,
                &quot;dischargeTime3&quot;: null,
                &quot;pv_on_off&quot;: null,
                &quot;pf_sys_year&quot;: null,
                &quot;pv_grid_voltage_high&quot;: null,
                &quot;pv_grid_voltage_low&quot;: null,
                &quot;mix_off_grid_enable&quot;: null,
                &quot;mix_ac_discharge_frequency&quot;: null,
                &quot;mix_ac_discharge_voltage&quot;: null,
                &quot;pv_pf_cmd_memory_state&quot;: null,
                &quot;pv_active_p_rate&quot;: null,
                &quot;pv_reactive_p_rate&quot;: null,
                &quot;pv_reactive_p_rate_two&quot;: null,
                &quot;backflow_setting&quot;: null,
                &quot;pv_power_factor&quot;: null,
                &quot;userName&quot;: null,
                &quot;modelText&quot;: &quot;A0B0DBT0PFU2M4S0&quot;,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;batSeriesNum&quot;: 0,
                &quot;batParallelNum&quot;: 0,
                &quot;ccCurrent&quot;: 0.0,
                &quot;lvVoltage&quot;: 0.0,
                &quot;cvVoltage&quot;: 0.0,
                &quot;failsafe&quot;: 0,
                &quot;gridFirstSwitch1&quot;: 0,
                &quot;gridFirstSwitch2&quot;: 0,
                &quot;gridFirstSwitch3&quot;: 0,
                &quot;batFirstSwitch1&quot;: 0,
                &quot;batFirstSwitch2&quot;: 0,
                &quot;batFirstSwitch3&quot;: 0,
                &quot;uwNominalGridVolt&quot;: 0.0,
                &quot;uwReconnectStartSlope&quot;: 0.0,
                &quot;uwLFRTEE&quot;: 0.0,
                &quot;uwHVRT2EE&quot;: 0.0,
                &quot;uwLVRT2EE&quot;: 0.0,
                &quot;uwHFRT2EE&quot;: 0.0,
                &quot;uwLFRT2EE&quot;: 0.0,
                &quot;uwLVRT3EE&quot;: 0.0,
                &quot;uwHVRTEE&quot;: 0.0,
                &quot;uwLVRTEE&quot;: 0.0,
                &quot;uwHFRTEE&quot;: 0.0,
                &quot;uwGridWattDelay&quot;: 0,
                &quot;uwHVRTTimeEE&quot;: 0,
                &quot;uwLVRTTimeEE&quot;: 0,
                &quot;uwHFRTTimeEE&quot;: 0,
                &quot;uwLFRTTimeEE&quot;: 0,
                &quot;uwHVRTTime2EE&quot;: 0,
                &quot;uwLVRTTime2EE&quot;: 0,
                &quot;uwHFRTTime2EE&quot;: 0,
                &quot;uwLFRTTime2EE&quot;: 0,
                &quot;uwLVRTTime3EE&quot;: 0,
                &quot;backUpEn&quot;: 0,
                &quot;sgipEn&quot;: 0,
                &quot;loadFirstStopSocSet&quot;: 0,
                &quot;invVersion&quot;: 0,
                &quot;forcedDischargeTimeStart4&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart5&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart6&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop4&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop5&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop6&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart4&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart5&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart6&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop4&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop5&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop6&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeStopSwitch4&quot;: 0,
                &quot;forcedDischargeStopSwitch5&quot;: 0,
                &quot;forcedDischargeStopSwitch6&quot;: 0,
                &quot;forcedChargeStopSwitch4&quot;: 0,
                &quot;forcedChargeStopSwitch5&quot;: 0,
                &quot;forcedChargeStopSwitch6&quot;: 0,
                &quot;batSerialNum&quot;: null,
                &quot;singleExport&quot;: 0,
                &quot;loadFirstControl&quot;: 0,
                &quot;mcVersion&quot;: &quot;null&quot;,
                &quot;monitorVersion&quot;: &quot;null&quot;,
                &quot;vppOpen&quot;: 0,
                &quot;batSysRateEnergy&quot;: -0.1,
                &quot;oldErrorFlag&quot;: 0,
                &quot;sysTimeText&quot;: &quot;2024-05-24 05:20:52&quot;,
                &quot;region&quot;: -1,
                &quot;v1&quot;: 122.0,
                &quot;v2&quot;: 119.0,
                &quot;v3&quot;: 146.0,
                &quot;v4&quot;: 143.0,
                &quot;inPower&quot;: 20.0,
                &quot;outPower&quot;: 20.0,
                &quot;reactiveDelay&quot;: 150.0,
                &quot;reactivePowerLimit&quot;: 48.0,
                &quot;safety&quot;: &quot;00&quot;,
                &quot;newSwVersionFlag&quot;: 0,
                &quot;offGridDischargeSOC&quot;: -1,
                &quot;safetyNum&quot;: &quot;4E&quot;,
                &quot;level&quot;: 4,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-24 15:27:33&quot;,
                &quot;children&quot;: null,
                &quot;treeName&quot;: &quot;OZD0849010&quot;,
                &quot;treeID&quot;: &quot;ST_OZD0849010&quot;,
                &quot;parentID&quot;: &quot;LIST_JAD084800B_96&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_green.gif&quot;,
                &quot;statusText&quot;: &quot;mix.status.normal&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-------------|:----|:------------|
| serialNum | String | Serial Number |
| portName | String | Communication Port Information (Type and Address) |
| dataLogSn | String | DataLog Serial Number |
| groupId = -1 | int | Inverter Group |
| alias | String | Alias |
| location | String | Location |
| addr = 0 | int | Inverter Address |
| fwVersion | String | Firmware Version |
| model | long | Model |
| innerVersion | String | Internal Version Number |
| lost = true | boolean | Communication Lost Status |
| status = -1 | int | Mix Status (0: Waiting Mode, 1: Self-check Mode, 3: Fault Mode, 4: Upgrading, 5-8: Normal Mode) |
| tcpServerIp | String | TCP Server IP Address |
| lastUpDateTime | Date | Last Update Time |
| sysTime | Calendar | System Time |
| deviceType | int | Device Type (0: Mix6k, 1: Mix4-10k) |
| communicationVersion | String | Communication Version Number |
| onOff | int | Power State (On/Off) |
| pmax | int | Rated Power |
| vnormal | float | Rated PV Voltage |
| lcdLanguage | int | LCD Language |
| countrySelected | int | Country Selection |
| wselectBaudrate | int | Baud Rate Selection |
| comAddress | int | Communication Address |
| manufacturer | String | Manufacturer Code |
| dtc | int | Device Code |
| modbusVersion | int | MODBUS Version |
| floatChargeCurrentLimit | float | Float Charge Current Limit |
| vbatWarning | float | Battery Low Voltage Warning Point |
| vbatWarnClr | float | Battery Low Voltage Recovery Point |
| vbatStopForDischarge | float | Battery Discharge Stop Voltage |
| vbatStopForCharge | float | Battery Charge Stop Voltage |
| vbatStartForDischarge | float | Battery Discharge Lower Limit Voltage |
| vbatStartforCharge | float | Battery Charge Upper Limit Voltage |
| batTempLowerLimitD | float | Battery Discharge Lower Temperature Limit |
| batTempUpperLimitD | float | Battery Discharge Upper Temperature Limit |
| batTempLowerLimitC | float | Battery Charge Lower Temperature Limit |
| batTempUpperLimitC | float | Battery Charge Upper Temperature Limit |
| forcedDischargeTimeStart1 | String | Forced Discharge Time 1 Start |
| forcedDischargeTimeStart2 | String | Forced Discharge Time 2 Start |
| forcedDischargeTimeStart3 | String | Forced Discharge Time 3 Start |
| forcedDischargeTimeStop1 | String | Forced Discharge Time 1 Stop |
| forcedDischargeTimeStop2 | String | Forced Discharge Time 2 Stop |
| forcedDischargeTimeStop3 | String | Forced Discharge Time 3 Stop |
| forcedChargeTimeStart1 | String | Forced Charge Time 1 Start |
| forcedChargeTimeStart2 | String | Forced Charge Time 2 Start |
| forcedChargeTimeStart3 | String | Forced Charge Time 3 Start |
| forcedChargeTimeStop1 | String | Forced Charge Time 1 Stop |
| forcedChargeTimeStop2 | String | Forced Charge Time 2 Stop |
| forcedChargeTimeStop3 | String | Forced Charge Time 3 Stop |
| bctMode | int | Sensor Type (2: METER; 1: cWirelessCT; 0: cWiredCT) |
| bctAdjust | int | Sensor Adjustment Enable |
| wdisChargeSOCLowLimit1 | int | Load Priority Mode Discharge |
| wdisChargeSOCLowLimit2 | int | Grid Priority Mode Discharge |
| wchargeSOCLowLimit1 | int | Load Priority Mode Charge |
| wchargeSOCLowLimit2 | int | Battery Priority Mode Charge |
| acChargeEnable | int | AC Charge Enable |
| priorityChoose | int | Energy Priority Selection |
| chargePowerCommand | int | Charge Power Setting |
| disChargePowerCommand | int | Discharge Power Setting |
| bagingTestStep | int | Battery Self-Test |
| batteryType | int | Battery Type Selection |
| epsFunEn | int | Emergency Power Supply Enable |
| epsVoltSet | int | Emergency Power Supply Voltage |
| epsFreqSet | int | Emergency Power Supply Frequency |
| forcedDischargeStopSwitch1 | int | Forced Discharge 1 Enable |
| forcedDischargeStopSwitch2 | int | Forced Discharge 2 Enable |
| forcedDischargeStopSwitch3 | int | Forced Discharge 3 Enable |
| forcedChargeStopSwitch1 | int | Forced Charge 1 Enable |
| forcedChargeStopSwitch2 | int | Forced Charge 2 Enable |
| forcedChargeStopSwitch3 | int | Forced Charge 3 Enable |
| voltageHighLimit | float | Utility Voltage Upper Limit |
| voltageLowLimit | float | Utility Voltage Lower Limit |
| buckUpsFunEn | int | Off-Grid Enable |
| uspFreqSet | int | Off-Grid Frequency |
| buckUPSVoltSet | int | Off-Grid Voltage |
| pvPfCmdMemoryState | int | Whether the Mix Inverter Stores the Following Commands |
| activeRate | int | Active Power |
| reactiveRate | int | Reactive Power |
| underExcited | int | Capacitive or Inductive |
| exportLimit | int | Anti-Backflow Enable |
| exportLimitPowerRate | float | Anti-Backflow |
| powerFactor | float | PF Value |
| pv_on_off | String | Power State (On/Off) |
| pf_sys_year | String | Set Time |
| pv_grid_voltage_high | String | Utility Voltage Upper Limit |
| pv_grid_voltage_low | String | Utility Voltage Lower Limit |
| mix_off_grid_enable | String | Off-Grid Enable |
| mix_ac_discharge_frequency | String | Off-Grid Frequency |
| mix_ac_discharge_voltage | String | Off-Grid Voltage |
| pv_pf_cmd_memory_state | String | Set Whether to Store the Following PF Commands |
| pv_active_p_rate | String | Set Active Power |
| pv_reactive_p_rate | String | Set Reactive Power |
| pv_reactive_p_rate_two | String | Reactive Power (Capacitive/Inductive) |
| backflow_setting | String | Anti-Backflow Setting |
| pv_power_factor | String | Set PF Value |
| batSeriesNum | int | Number of Battery Series |
| batParallelNum | int | Number of Battery Parallel |

**Remarks**
- The retrieval frequency is once every 5 minutes or less.

---

# 20. sph Last Detailed Data

*Page ID: `11292922052386278`*

  
**Brief Description:**

- Data format and parameter description for the last detailed data of sph equipment.
- `Only applicable to: Batch retrieval of the last data for devices.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;sph&quot;: [
            {
                &quot;serialNum&quot;: &quot;OZD0849010&quot;,
                &quot;dataLogSn&quot;: &quot;JAD084800B&quot;,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716618931362,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 5,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 1318.9,
                &quot;vpv1&quot;: 222.8,
                &quot;ppv1&quot;: 705.4,
                &quot;vpv2&quot;: 200.7,
                &quot;ppv2&quot;: 613.5,
                &quot;pac&quot;: 1258.1,
                &quot;fac&quot;: 50.04,
                &quot;vac1&quot;: 239.1,
                &quot;pac1&quot;: 1257.0,
                &quot;eacToday&quot;: 8.6,
                &quot;eacTotal&quot;: 1714.4,
                &quot;timeTotal&quot;: 1.35345745E7,
                &quot;epv1Today&quot;: 5.2,
                &quot;epv1Total&quot;: 1029.7,
                &quot;epv2Today&quot;: 4.4,
                &quot;epv2Total&quot;: 923.7,
                &quot;epvTotal&quot;: 1953.4,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 1,
                &quot;batteryType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 5,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;pdischarge1&quot;: 5.8,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 55.2,
                &quot;soc&quot;: 100,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 17.8,
                &quot;pacToGridTotal&quot;: 17.8,
                &quot;plocalLoadR&quot;: 1243.2,
                &quot;plocalLoadTotal&quot;: 1243.2,
                &quot;batteryTemperature&quot;: 0.0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.3,
                &quot;etogridTotal&quot;: 59.6,
                &quot;edischarge1Today&quot;: 0.2,
                &quot;edischarge1Total&quot;: 7.3,
                &quot;echarge1Today&quot;: 0.0,
                &quot;echarge1Total&quot;: 29.3,
                &quot;elocalLoadToday&quot;: 1797.9,
                &quot;elocalLoadTotal&quot;: 393917.0,
                &quot;upsFac&quot;: 0.0,
                &quot;upsVac1&quot;: 0.0,
                &quot;upsPac1&quot;: 0.0,
                &quot;upsLoadpercent&quot;: 0,
                &quot;upsPF&quot;: 1000.0,
                &quot;bmsStatusOld&quot;: 0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsErrorOld&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;bmsSOC&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsMaxDischgCurr&quot;: 0.0,
                &quot;bmsGaugeRM&quot;: 0.0,
                &quot;bmsGaugeFCC&quot;: 0,
                &quot;bmsFW&quot;: 0,
                &quot;bmsDeltaVolt&quot;: 0.0,
                &quot;bmsCycleCnt&quot;: 0,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0.0,
                &quot;bmsWarnInfoOld&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsMCUVersion&quot;: 0,
                &quot;bmsInfo&quot;: 0,
                &quot;bmsPackInfo&quot;: 0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCell1Volt&quot;: 0.0,
                &quot;bmsCell2Volt&quot;: 0.0,
                &quot;bmsCell3Volt&quot;: 0.0,
                &quot;bmsCell4Volt&quot;: 0.0,
                &quot;bmsCell5Volt&quot;: 0.0,
                &quot;bmsCell6Volt&quot;: 0.0,
                &quot;bmsCell7Volt&quot;: 0.0,
                &quot;bmsCell8Volt&quot;: 0.0,
                &quot;bmsCell9Volt&quot;: 0.0,
                &quot;bmsCell10Volt&quot;: 0.0,
                &quot;bmsCell11Volt&quot;: 0.0,
                &quot;bmsCell12Volt&quot;: 0.0,
                &quot;bmsCell13Volt&quot;: 0.0,
                &quot;bmsCell14Volt&quot;: 0.0,
                &quot;bmsCell15Volt&quot;: 0.0,
                &quot;bmsCell16Volt&quot;: 0.0,
                &quot;acChargeEnergyToday&quot;: 0.0,
                &quot;acChargeEnergyTotal&quot;: 0.0,
                &quot;acChargePower&quot;: 0.0,
                &quot;vBus1&quot;: 380.5,
                &quot;vBus2&quot;: 312.9,
                &quot;temp1&quot;: 35.0,
                &quot;temp2&quot;: 31.800001,
                &quot;temp3&quot;: 35.7,
                &quot;vBatDsp&quot;: 55.2,
                &quot;sysEn&quot;: 416,
                &quot;vac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsVac3&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;upsPac3&quot;: 0.0,
                &quot;bmsProtection&quot;: 0,
                &quot;bmsErrorExpansion&quot;: 0,
                &quot;maxSingleCellVoltNo&quot;: 0,
                &quot;minSingleCellVoltNo&quot;: 0,
                &quot;maxSingleCellTemNo&quot;: 0,
                &quot;minSingleCellTemNo&quot;: 0,
                &quot;moduleQty&quot;: 0,
                &quot;moduleSeriesQty&quot;: 0,
                &quot;chargeForbiddenMark&quot;: 0,
                &quot;dischargeForbiddenMark&quot;: 0,
                &quot;softwareMajorVersion&quot;: 0,
                &quot;softwareMinorVersion&quot;: 0,
                &quot;softwareDevelopMajorVersion&quot;: 0,
                &quot;softwareDevelopMinorVersion&quot;: 0,
                &quot;chargeCutoffVolt&quot;: 0.0,
                &quot;dischargeCutoffVolt&quot;: 0.0,
                &quot;maxSingleCellVolt&quot;: 0.0,
                &quot;minSingleCellVolt&quot;: 0.0,
                &quot;maxSingleCellTem&quot;: 0.0,
                &quot;minSingleCellTem&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;capacityADD&quot;: 0.0,
                &quot;backupWarning&quot;: 0,
                &quot;sgipCyclCnt&quot;: 0,
                &quot;uwBatCycleCntPre&quot;: 0,
                &quot;sgipStartCyclCnt&quot;: 0,
                &quot;dsgipStartDateTime&quot;: null,
                &quot;batErrorUnion&quot;: 0,
                &quot;esystemtoday&quot;: -0.10000000149011612,
                &quot;esystemtotal&quot;: -0.10000000149011612,
                &quot;eselftoday&quot;: -0.10000000149011612,
                &quot;eselftotal&quot;: -0.10000000149011612,
                &quot;psystem&quot;: -0.10000000149011612,
                &quot;pself&quot;: -0.10000000149011612,
                &quot;epvtoday&quot;: 9.600000381469727,
                &quot;uwMaxCellVol&quot;: -0.0010000000474974513,
                &quot;uwMinCellVol&quot;: -0.0010000000474974513,
                &quot;bModuleNum&quot;: -1,
                &quot;bTotalCellNum&quot;: -1,
                &quot;uwMaxVoltCellNo&quot;: -1,
                &quot;uwMinVoltCellNo&quot;: -1,
                &quot;uwMaxTemprCell&quot;: -0.10000000149011612,
                &quot;uwMinTemprCell&quot;: -0.10000000149011612,
                &quot;uwMaxTemprCellNo&quot;: -1,
                &quot;uwMinTemprCellNo&quot;: -1,
                &quot;protectPackId&quot;: -1,
                &quot;maxSOC&quot;: -1,
                &quot;minSOC&quot;: -1,
                &quot;bmsError2&quot;: -1,
                &quot;bmsError3&quot;: -1,
                &quot;bmsWarnInfo2&quot;: -1,
                &quot;bmsHighestSoftVersion&quot;: -1,
                &quot;bmsHardwareVersion&quot;: -1,
                &quot;bmsRequestType&quot;: -1,
                &quot;accDischargePackSn&quot;: -1,
                &quot;accdischargePower&quot;: -0.1,
                &quot;accChargePackSn&quot;: -1,
                &quot;accChargePower&quot;: -0.1,
                &quot;firstBattFaultSn&quot;: -1,
                &quot;secondBattFaultSn&quot;: -1,
                &quot;thirdBattFaultSn&quot;: -1,
                &quot;fourthBattFaultSn&quot;: -1,
                &quot;battHistoryFaultCode1&quot;: -1,
                &quot;battHistoryFaultCode2&quot;: -1,
                &quot;battHistoryFaultCode3&quot;: -1,
                &quot;battHistoryFaultCode4&quot;: -1,
                &quot;battHistoryFaultCode5&quot;: -1,
                &quot;battHistoryFaultCode6&quot;: -1,
                &quot;battHistoryFaultCode7&quot;: -1,
                &quot;battHistoryFaultCode8&quot;: -1,
                &quot;numberOfBattCodes&quot;: -1,
                &quot;pex&quot;: 0.0,
                &quot;eexToday&quot;: 0.0,
                &quot;eexTotal&quot;: 0.0,
                &quot;pmR&quot;: 0,
                &quot;pmS&quot;: 0,
                &quot;pmT&quot;: 0,
                &quot;pacR&quot;: 0,
                &quot;pacS&quot;: 0,
                &quot;pacT&quot;: 0,
                &quot;plocalLoadR2&quot;: 0,
                &quot;plocalLoadS&quot;: 0,
                &quot;plocalLoadT&quot;: 0,
                &quot;uwDspInvDebugData&quot;: -1,
                &quot;uwDspInvDebugData1&quot;: -1,
                &quot;uwDspInvDebugData2&quot;: -1,
                &quot;uwDspInvDebugData3&quot;: -1,
                &quot;uwDspInvDebugData4&quot;: -1,
                &quot;uwDspDcDcDebugData&quot;: -1,
                &quot;uwDspDcDcDebugData1&quot;: -1,
                &quot;uwDspDcDcDebugData2&quot;: -1,
                &quot;uwDspDcDcDebugData3&quot;: -1,
                &quot;uwDspDcDcDebugData4&quot;: -1,
                &quot;bmsHardwareVersion2&quot;: 0,
                &quot;mixBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-05-25 14:35:31&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;PV Bat Online&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;ppvText&quot;: &quot;1318.9 W&quot;,
                &quot;socText&quot;: &quot;100%&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Type      | Parameter Name        | Description                                                  |
|-----------|-----------------------|--------------------------------------------------------------|
| String    | serialNum             | Serial Number                                                |
| Calendar  | calendar              | Time                                                         |
| boolean   | withTime              | Whether the incoming data includes time                      |
| int       | status = 0            | 0.Power-on 1.Stand-by 2.Bypass 3.Grid-on 4.Grid-off 5.Fault 6.Flash 7.Turn-off                   |
| boolean   | isAgain               | Whether it is a retransmission                               |
| boolean   | lost = true           | Whether communication is lost                                |
| ppv | double | Total PV input power |
| ppv1 | double | PV1 input power |
| ppv2 | double | PV2 input power |
| ppv3 | double | PV3 input power |
| vpv1 | float | PV1 voltage |
| vpv2 | float | PV2 voltage |
| vpv3 | float | PV3 voltage |
| ipv1 | float | PV1 current |
| ipv2 | float | PV2 current |
| ipv3 | float | PV3 current |
| pac | double | Inverter output power |
| fac | float | Grid frequency |
| vac1 | float | Grid voltage (single/three phase) |
| iac1 | float | Grid output current |
| pac1 | double | Grid output power (single/three phase) |
| vac2 | float | Grid voltage (three phase) |
| iac2 | float | Grid output current (three phase) |
| pac2 | double | Grid output power (three phase) |
| eacToday | float | Inverter daily energy generation |
| eacTotal | double | Inverter total energy generation |
| timeTotal | double | Total operating time |
| epv1Today | float | PV1 daily energy |
| epv1Total | double | PV1 total energy |
| epv2Today | float | PV2 daily energy |
| epv2Total | double | PV2 total energy |
| epv3Today | double | PV3 daily energy |
| epv3Total | double | PV3 total energy |
| epvToday | double | Total PV daily energy |
| epvTotal | double | Total PV energy |
| pf | float | Power factor |
| faultCode | int | Main inverter fault code |
| faultBitCode | int | Inverter fault bit code |
| systemFault | int | System fault code |
| systemWarn | int | System warning code |
| warnCode1 | int | Sub warning code |
| warnCode | int | Main warning code |
| priorityChoose | int | Priority mode (0: load, 1: grid, 2: battery) |
| uwSysWorkMode | int | System working mode |
| sysFaultWord | int | System fault word 0 |
| sysFaultWord1 | int | System fault word 1 |
| sysFaultWord2 | int | System fault word 2 |
| sysFaultWord3 | int | System fault word 3 |
| sysFaultWord4 | int | System fault word 4 |
| sysFaultWord5 | int | System fault word 5 |
| sysFaultWord6 | int | System fault word 6 |
| sysFaultWord7 | int | System fault word 7 |
| pdischarge1 | double | Battery discharge power |
| pcharge1 | double | Battery charge power |
| vbat | float | Battery voltage |
| soc | int | Battery state of charge |
| pacToUserR | double | Grid-to-load power |
| pacToUserTotal | double | Total grid-to-load power |
| pacToGridR | double | Power fed to grid |
| pacToGridS | double | Power fed to grid |
| pacToGridTotal | double | Total power fed to grid |
| plocalLoadR | double | Local load power |
| plocalLoadS | double | Local load power |
| plocalLoadTotal | double | Total local load power |
| spStatus | int | SP status |
| etoUserToday | double | Daily energy supplied from grid |
| etoUserTotal | double | Total energy supplied from grid |
| etoGridToday | double | Daily energy fed into grid |
| etoGridTotal | double | Total energy fed into grid |
| edischarge1Today | double | Battery daily discharge energy |
| edischarge1Total | double | Battery total discharge energy |
| echarge1Today | double | Battery daily charge energy |
| echarge1Total | double | Battery total charge energy |
| elocalLoadToday | double | Daily local load energy consumption |
| elocalLoadTotal | double | Total local load energy consumption |
| upsFac | float | UPS frequency |
| upsVac1 | float | UPS voltage |
| epsIac1 | float | R-phase output current |
| upsPac1 | double | UPS apparent output power |
| epsVac2 | float | Off-grid S-phase voltage |
| epsIac2 | float | S-phase output current |
| upsPac2 | double | Off-grid side power |
| bmsSOC | int | Battery state of charge |
| bmsBatteryVolt | float | Battery voltage |
| bmsBatteryCurr | float | Battery current |
| bmsBatteryTemp | float | Battery temperature |
| bmsSOH | int | Battery state of health |
| bmsConstantVolt | float | Battery constant voltage point |
| bmsUsingCap | int | Battery pack capacity type |
| pex | double | PV inverter power |
| esystemtoday | double | System daily energy generation (kWh) |
| esystemtotal | double | System total energy generation (kWh) |
| eselftoday | double | Self-consumption daily energy (kWh) |
| eselftotal | double | Self-consumption total energy (kWh) |
| psystem | double | System generation power (W) |
| pself | double | Self-consumption power (W) |
| sysStatus | int | Inverter operating status |
| dcTemp | float | DC temperature |
| invTemp | float | Inverter temperature |
| gridStatus | int | Grid status |
| genPower | float | Generator power |
| genVol | float | Generator voltage |
| genCurr | float | Generator current |
| genFreq | float | Generator frequency |
| genEnergy | float | Generator energy |
| rLocalEnergy | double | R-phase local load energy |
| sLocalEnergy | double | S-phase local load energy |
| chipType | int | Chip type |
| genEnergyToday | double | Generator daily energy |
| loadPower1 | float | Load power 1 |
| loadPower2 | float | Load power 2 |
| rLoadVol | float | Load voltage 1 |
| sLoadVol | float | Load voltage 2 |
| esystemHour | double | System hourly energy |
| esystemMonth | double | System monthly energy |
| esystemYear | double | System yearly energy |
| eselfHour | double | Self-consumption hourly energy |
| eselfMonth | double | Self-consumption monthly energy |
| eselfYear | double | Self-consumption yearly energy |
| eToGridHour | double | Energy fed into grid (hour) |
| eToGridMonth | double | Energy fed into grid (month) |
| eToGridYear | double | Energy fed into grid (year) |
| eToUserHour | double | Energy imported from grid (hour) |
| eToUserMonth | double | Energy imported from grid (month) |
| eToUserYear | double | Energy imported from grid (year) |
| elocalLoadHour | double | Local load energy (hour) |
| elocalLoadMonth | double | Local load energy (month) |
| elocalLoadYear | double | Local load energy (year) |
| epvHour | double | PV hourly energy |
| epvMonth | double | PV monthly energy |
| epvYear | double | PV yearly energy |
| batPower | float | Battery power (locally measured) |
| vbat1 | float | Battery voltage (locally measured) |
| ibat | float | Battery current |
| m1Version | String | Control firmware version 1 |
| m2Version | String | Control firmware version 2 |
| hmiVersion | String | HMI firmware version |
| temp1 | float | Inverter temperature |
| temp2 | float | Internal IPM temperature |
| temp3 | float | BOOST temperature |
| pBusVoltage | float | P-bus internal voltage |
| nBusVoltage | float | N-bus internal voltage |
| lCDFaultNum | int | LCD displayed fault code |
| lCDWarnNum | int | LCD displayed warning code |
| lCDVersion | String | LCD software version |
| bMSVersion | String | BMS firmware version |
| bMSSn | String | BMS serial number |
| bMSStatus | int | Battery status |
| bMSMaxDischargeCurr | float | BMS maximum discharge current |
| bMSMaxChargeCurr | float | BMS maximum charge current |
| bMSGaugeRM | float | BMS Gauge remaining capacity |
| bMSGaugeFCC | float | BMS Gauge full charge capacity |
| batDePowerReason | int | Battery power derating reason |
| bMSDeltaVolt | float | BMS cell voltage delta |
| bMSCycleCnt | int | BMS cycle count |
| BMSInfo | int | BMS information |
| bMSPackInfo | int | BMS pack information |
| moduleNum | int | Number of battery modules |
| totalCellNumber | int | Total number of battery cells |
| batProtect1To2 | int | Battery protection 1–2 |
| batProtect3To4 | int | Battery protection 3–4 |
| batProtect5 | int | Battery protection 5 |
| batWarnInfo1To2 | int | Battery warning 1–2 |
| batWarnInfo3 | int | Battery warning 3 |
| protectPackID | int | Fault battery pack ID |
| maxCellVol | float | Maximum cell voltage |
| minCellVol | float | Minimum cell voltage |
| maxVoltCellNo | int | Cell number with maximum voltage |
| minVoltCellNo | int | Cell number with minimum voltage |
| maxTempCell | float | Maximum cell temperature |
| minTempCell | float | Minimum cell temperature |
| maxTempCellNo | int | Cell number with maximum temperature |
| minTempCellNo | int | Cell number with minimum temperature |
| maxSOC | int | Maximum SOC in parallel system |
| minSOC | int | Minimum SOC in parallel system |
| doStatus | int | Digital output status |
| dsgBatNumber | int | Battery number for discharge statistics |
| bMSDsgEnergy | float | BMS discharge energy |
| chgBatNumber | int | Battery number for charge statistics |
| bMSChgEnergy | float | BMS charge energy |
| bMSRequestType | int | Battery request information |

**Remarks**
- The retrieval frequency is once every 5 minutes.

---

# 21. sph Device Historical Data

*Page ID: `11292922712705121`*

**Brief Description:**

- Data format and parameter description of the historical data of the sph device
- `Applicable only: to retrieve all detailed data of a specific device for a specific day.`

**Return Example**

``` 
&quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-23&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;OZD0849010&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716565951000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 0.0,
                &quot;vpv1&quot;: 0.0,
                &quot;ppv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;pac&quot;: 4.1,
                &quot;fac&quot;: 50.01,
                &quot;vac1&quot;: 237.0,
                &quot;pac1&quot;: 4.1,
                &quot;eacToday&quot;: 21.2,
                &quot;eacTotal&quot;: 1705.8,
                &quot;timeTotal&quot;: 1.3482293E7,
                &quot;epv1Today&quot;: 12.5,
                &quot;epv1Total&quot;: 1024.5,
                &quot;epv2Today&quot;: 10.5,
                &quot;epv2Total&quot;: 919.3,
                &quot;epvTotal&quot;: 1943.8,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 1,
                &quot;batteryType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 6,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 32,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;pdischarge1&quot;: 13.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 55.2,
                &quot;soc&quot;: 100,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 17.1,
                &quot;pacToGridTotal&quot;: 17.1,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 0.0,
                &quot;batteryTemperature&quot;: 250.0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.4,
                &quot;etogridTotal&quot;: 59.3,
                &quot;edischarge1Today&quot;: 0.2,
                &quot;edischarge1Total&quot;: 7.1,
                &quot;echarge1Today&quot;: 0.0,
                &quot;echarge1Total&quot;: 29.3,
                &quot;elocalLoadToday&quot;: 2526.2,
                &quot;elocalLoadTotal&quot;: 392119.1,
                &quot;upsFac&quot;: 0.0,
                &quot;upsVac1&quot;: 0.0,
                &quot;upsPac1&quot;: 0.0,
                &quot;upsLoadpercent&quot;: 0,
                &quot;upsPF&quot;: 1000.0,
                &quot;bmsStatusOld&quot;: 0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsErrorOld&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;bmsSOC&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsMaxDischgCurr&quot;: 0.0,
                &quot;bmsGaugeRM&quot;: 0.0,
                &quot;bmsGaugeFCC&quot;: 0,
                &quot;bmsFW&quot;: 0,
                &quot;bmsDeltaVolt&quot;: 0.0,
                &quot;bmsCycleCnt&quot;: 0,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0.0,
                &quot;bmsWarnInfoOld&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsMCUVersion&quot;: 0,
                &quot;bmsInfo&quot;: 0,
                &quot;bmsPackInfo&quot;: 0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCell1Volt&quot;: 0.0,
                &quot;bmsCell2Volt&quot;: 0.0,
                &quot;bmsCell3Volt&quot;: 0.0,
                &quot;bmsCell4Volt&quot;: 0.0,
                &quot;bmsCell5Volt&quot;: 0.0,
                &quot;bmsCell6Volt&quot;: 0.0,
                &quot;bmsCell7Volt&quot;: 0.0,
                &quot;bmsCell8Volt&quot;: 0.0,
                &quot;bmsCell9Volt&quot;: 0.0,
                &quot;bmsCell10Volt&quot;: 0.0,
                &quot;bmsCell11Volt&quot;: 0.0,
                &quot;bmsCell12Volt&quot;: 0.0,
                &quot;bmsCell13Volt&quot;: 0.0,
                &quot;bmsCell14Volt&quot;: 0.0,
                &quot;bmsCell15Volt&quot;: 0.0,
                &quot;bmsCell16Volt&quot;: 0.0,
                &quot;acChargeEnergyToday&quot;: 0.0,
                &quot;acChargeEnergyTotal&quot;: 0.0,
                &quot;acChargePower&quot;: 0.0,
                &quot;vBus1&quot;: 387.0,
                &quot;vBus2&quot;: 313.0,
                &quot;temp1&quot;: 29.0,
                &quot;temp2&quot;: 29.0,
                &quot;temp3&quot;: 28.0,
                &quot;vBatDsp&quot;: 55.2,
                &quot;sysEn&quot;: 416,
                &quot;vac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsVac3&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;upsPac3&quot;: 0.0,
                &quot;bmsProtection&quot;: 0,
                &quot;bmsErrorExpansion&quot;: 0,
                &quot;maxSingleCellVoltNo&quot;: 0,
                &quot;minSingleCellVoltNo&quot;: 0,
                &quot;maxSingleCellTemNo&quot;: 0,
                &quot;minSingleCellTemNo&quot;: 0,
                &quot;moduleQty&quot;: 0,
                &quot;moduleSeriesQty&quot;: 0,
                &quot;chargeForbiddenMark&quot;: 0,
                &quot;dischargeForbiddenMark&quot;: 0,
                &quot;softwareMajorVersion&quot;: 0,
                &quot;softwareMinorVersion&quot;: 0,
                &quot;softwareDevelopMajorVersion&quot;: 0,
                &quot;softwareDevelopMinorVersion&quot;: 0,
                &quot;chargeCutoffVolt&quot;: 0.0,
                &quot;dischargeCutoffVolt&quot;: 0.0,
                &quot;maxSingleCellVolt&quot;: 0.0,
                &quot;minSingleCellVolt&quot;: 0.0,
                &quot;maxSingleCellTem&quot;: 0.0,
                &quot;minSingleCellTem&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;capacityADD&quot;: 0.0,
                &quot;backupWarning&quot;: 0,
                &quot;sgipCyclCnt&quot;: 0,
                &quot;uwBatCycleCntPre&quot;: 0,
                &quot;sgipStartCyclCnt&quot;: 0,
                &quot;dsgipStartDateTime&quot;: &quot;null&quot;,
                &quot;batErrorUnion&quot;: 0,
                &quot;esystemtoday&quot;: -0.10000000149011612,
                &quot;esystemtotal&quot;: -0.10000000149011612,
                &quot;eselftoday&quot;: -0.10000000149011612,
                &quot;eselftotal&quot;: -0.10000000149011612,
                &quot;psystem&quot;: -0.10000000149011612,
                &quot;pself&quot;: -0.10000000149011612,
                &quot;epvtoday&quot;: 23.0,
                &quot;uwMaxCellVol&quot;: -0.0010000000474974513,
                &quot;uwMinCellVol&quot;: -0.0010000000474974513,
                &quot;bModuleNum&quot;: -1,
                &quot;bTotalCellNum&quot;: -1,
                &quot;uwMaxVoltCellNo&quot;: -1,
                &quot;uwMinVoltCellNo&quot;: -1,
                &quot;uwMaxTemprCell&quot;: -0.10000000149011612,
                &quot;uwMinTemprCell&quot;: -0.10000000149011612,
                &quot;uwMaxTemprCellNo&quot;: -1,
                &quot;uwMinTemprCellNo&quot;: -1,
                &quot;protectPackId&quot;: -1,
                &quot;maxSOC&quot;: -1,
                &quot;minSOC&quot;: -1,
                &quot;bmsError2&quot;: -1,
                &quot;bmsError3&quot;: -1,
                &quot;bmsWarnInfo2&quot;: -1,
                &quot;bmsHighestSoftVersion&quot;: -1,
                &quot;bmsHardwareVersion&quot;: -1,
                &quot;bmsRequestType&quot;: -1,
                &quot;accDischargePackSn&quot;: -1,
                &quot;accdischargePower&quot;: -0.1,
                &quot;accChargePackSn&quot;: -1,
                &quot;accChargePower&quot;: -0.1,
                &quot;firstBattFaultSn&quot;: -1,
                &quot;secondBattFaultSn&quot;: -1,
                &quot;thirdBattFaultSn&quot;: -1,
                &quot;fourthBattFaultSn&quot;: -1,
                &quot;battHistoryFaultCode1&quot;: -1,
                &quot;battHistoryFaultCode2&quot;: -1,
                &quot;battHistoryFaultCode3&quot;: -1,
                &quot;battHistoryFaultCode4&quot;: -1,
                &quot;battHistoryFaultCode5&quot;: -1,
                &quot;battHistoryFaultCode6&quot;: -1,
                &quot;battHistoryFaultCode7&quot;: -1,
                &quot;battHistoryFaultCode8&quot;: -1,
                &quot;numberOfBattCodes&quot;: -1,
                &quot;pex&quot;: 0.0,
                &quot;eexToday&quot;: 0.0,
                &quot;eexTotal&quot;: 0.0,
                &quot;pmR&quot;: 0,
                &quot;pmS&quot;: 0,
                &quot;pmT&quot;: 0,
                &quot;pacR&quot;: 0,
                &quot;pacS&quot;: 0,
                &quot;pacT&quot;: 0,
                &quot;plocalLoadR2&quot;: 0,
                &quot;plocalLoadS&quot;: 0,
                &quot;plocalLoadT&quot;: 0,
                &quot;uwDspInvDebugData&quot;: -1,
                &quot;uwDspInvDebugData1&quot;: -1,
                &quot;uwDspInvDebugData2&quot;: -1,
                &quot;uwDspInvDebugData3&quot;: -1,
                &quot;uwDspInvDebugData4&quot;: -1,
                &quot;uwDspDcDcDebugData&quot;: -1,
                &quot;uwDspDcDcDebugData1&quot;: -1,
                &quot;uwDspDcDcDebugData2&quot;: -1,
                &quot;uwDspDcDcDebugData3&quot;: -1,
                &quot;uwDspDcDcDebugData4&quot;: -1,
                &quot;bmsHardwareVersion2&quot;: 0,
                &quot;mixBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-05-24 23:52:31&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Bat Online&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;ppvText&quot;: &quot;0.0 W&quot;,
                &quot;socText&quot;: &quot;100%&quot;
            }
         ],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

|Type|Parameter Name|Description|
|:-----  |:-----|----- |
| String | serialNum | Serial Number
| Calendar | calendar | Time
| boolean | withTime | Whether the received data contains time
| int | status = 0 | Mix Status 0: waiting, 1: normal, 2: fault
| boolean | isAgain | Whether it is a re-transmission
| boolean | lost = true | Whether communication is lost
| String | ppv | Total PV input power
| String | vpv1 | PV1 input voltage
| String | ppv1 | PV1 input power
| String | vpv2 | PV2 input voltage
| String | ppv2 | PV2 input power
| String | pac | Inverter output power
| String | fac | Grid frequency
| String | vac1 | Grid voltage
| String | pac1 | Inverter apparent output power
| String | eacToday | Inverter daily output energy
| String | eacTotal | Inverter total output energy
| String | timeTotal; | Total running time
| String | epv1Today | PV1 daily energy generation
| String | epv1Total | PV1 total energy generation
| String | epv2Today | PV2 daily energy generation
| String | epv2Total | PV2 total energy generation
| String | epvTotal | Total PV energy generation
| int | faultCode | Inverter fault code
| int | faultBitCode | Inverter fault bit code
| int | warnCode | Warning code
| int | errorCode | Error code
| int | uwSysWorkMode | System working mode
| String | pdischarge1 | Battery discharge power
| String | pcharge1 | Battery charge power
| String | vbat | Battery voltage
| String | soc | Battery state of charge
| String | pacToUserR | Grid forward power
| String | pacToUserTotal | Total grid forward power
| String | pacToGridR | Grid reverse power
| String | pacToGridTotal | Total grid reverse power
| String | plocalLoadR | Local load power consumption
| String | plocalLoadTotal | Total local load power consumption
| String | batteryTemperature | Battery temperature
| String | etoUserToday | Grid daily output energy
| String | etoUserTotal | Total grid output energy
| String | etoGridToday | Grid daily input energy
| String | etogridTotal | Total grid input energy
| String | edischarge1Today | Battery daily discharge energy
| String | edischarge1Total | Total battery discharge energy
| String | echarge1Today | Battery daily charge energy
| String | echarge1Total | Total battery charge energy
| String | elocalLoadToday | Local load daily energy consumption
| String | elocalLoadTotal | Total local load energy consumption
| String | upsFac | UPS frequency
| String | upsVac1 | UPS voltage
| String | upsPac1 | UPS apparent output power
| String | upsLoadpercent | UPS load percentage
| String | upsPF | UPS power factor
| int | bmsStatusOld | Battery historical status
| int | bmsStatus | Battery status
| int | bmsErrorOld | Battery historical fault
| int | bmsError | Battery fault
| String | bmsSOC | Battery state of charge
| String | bmsBatteryVolt | Battery voltage
| String | bmsBatteryCurr | Battery current
| String | bmsBatteryTemp | Battery temperature
| String | bmsMaxCurr | Maximum charge/discharge current
| String | bmsMaxDischgCurr | Maximum discharge current
| String | bmsGaugeRM | System capacity
| String | bmsGaugeFCC | Rated capacity
| int | bmsFW | BMS firmware version number
| float | bmsDeltaVolt | Voltage difference between battery cells
| int | bmsCycleCnt | Battery cycle count
| int | bmsSOH | Battery state of health
| float | bmsConstantVolt | Battery constant voltage charging point
| int | bmsWarnInfoOld | Battery historical warning information
| int | bmsWarnInfo | Battery warning information
| int | bmsMCUVersion | BMS firmware version
| int | bmsInfo | BMS information
| int | bmsPackInfo | Battery pack information
| int | bmsUsingCap | Battery pack power type
| String | bmsCell1Volt | Battery cell 1 voltage
| String | bmsCell2Volt | Battery cell 2 voltage
| String | bmsCell3Volt | Battery cell 3 voltage
| String | bmsCell4Volt | Battery cell 4 voltage
| String | bmsCell5Volt | Battery cell 5 voltage
| String | bmsCell6Volt | Battery cell 6 voltage
| String | bmsCell7Volt | Battery cell 7 voltage
| String | bmsCell8Volt | Battery cell 8 voltage
| String | bmsCell9Volt | Battery cell 9 voltage
| String | bmsCell10Volt | Battery cell 10 voltage
| String | bmsCell11Volt | Battery cell 11 voltage
| String | bmsCell12Volt | Battery cell 12 voltage
| String | bmsCell13Volt | Battery cell 13 voltage
| String | bmsCell14Volt | Battery cell 14 voltage
| String | bmsCell15Volt | Battery cell 15 voltage
| String | bmsCell16Volt | Battery cell 16 voltage
| String | acChargeEnergyToday | AC daily charge energy
| String | acChargeEnergyTotal | Total AC charge energy
| String | acChargePower | AC charge power
| String | vBus1 | Bus 1 voltage
| String | vBus2 | Bus 2 voltage
| String | temp1 | Temperature 1
| String | temp2 | Temperature 2
| String | temp3 | Temperature 3
| String | vBatDsp | DSP collected battery voltage
| int | sysEn | System enable bit
| String | vac2 | AC side phase S voltage
| String | pac2 | AC side power
| String | vac3 | AC side phase T voltage
| String | pac3 | AC side power
| String | epsVac2 | Off-grid side phase S voltage
| String | epsVac3 | Off-grid side phase T voltage
| String | upsPac2 | Off-grid side power
| String | upsPac3 | Off-grid side power

**Notes**
- Retrieval frequency is once every 5 minutes

---

# 22. Max Basic Information

*Page ID: `11292919260348864`*

**Brief Description:**

- Data return format for basic information of max devices and explanation of some parameters of the basic information.
- `Only applicable for: Batch retrieval of basic device information.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;max&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;serialNum&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;bigDevice&quot;: false,
                &quot;portName&quot;: &quot;ShinePano - BLE4BEQ0BW&quot;,
                &quot;dataLogSn&quot;: &quot;BLE4BEQ0BW&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;TJ1.0&quot;,
                &quot;model&quot;: 720575940631003386,
                &quot;innerVersion&quot;: &quot;TJAA08020002&quot;,
                &quot;lost&quot;: false,
                &quot;status&quot;: 1,
                &quot;tcpServerIp&quot;: &quot;47.119.22.101&quot;,
                &quot;lastUpdateTime&quot;: 1716534733000,
                &quot;normalPower&quot;: 25000,
                &quot;power&quot;: 0.0,
                &quot;communicationVersion&quot;: &quot;ZBab-0002&quot;,
                &quot;deviceType&quot;: 1,
                &quot;eToday&quot;: 0.0,
                &quot;eTotal&quot;: 0.0,
                &quot;energyDayMap&quot;: {},
                &quot;energyMonth&quot;: 0.0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;userName&quot;: null,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;modelText&quot;: &quot;S0AB00D00T00P0FU01M00FA&quot;,
                &quot;timezone&quot;: 8.0,
                &quot;sysTime&quot;: null,
                &quot;onOff&quot;: 0,
                &quot;activeRate&quot;: 0,
                &quot;reactiveRate&quot;: 0,
                &quot;pvPfCmdMemoryState&quot;: 0,
                &quot;pf&quot;: 0.0,
                &quot;exportLimit&quot;: 0,
                &quot;exportLimitPowerRate&quot;: 0.0,
                &quot;voltageHighLimit&quot;: 0.0,
                &quot;voltageLowLimit&quot;: 0.0,
                &quot;frequencyHighLimit&quot;: 0.0,
                &quot;frequencyLowLimit&quot;: 0.0,
                &quot;backflowDefaultPower&quot;: 0.0,
                &quot;lcdLanguage&quot;: 0,
                &quot;pfModel&quot;: 0,
                &quot;pflinep1_lp&quot;: 0,
                &quot;pflinep1_pf&quot;: 0.0,
                &quot;pflinep2_lp&quot;: 0,
                &quot;pflinep2_pf&quot;: 0.0,
                &quot;pflinep3_lp&quot;: 0,
                &quot;pflinep3_pf&quot;: 0.0,
                &quot;pflinep4_lp&quot;: 0,
                &quot;pflinep4_pf&quot;: 0.0,
                &quot;strNum&quot;: 0,
                &quot;vacLow&quot;: 0.0,
                &quot;vacHigh&quot;: 0.0,
                &quot;facLow&quot;: 0.0,
                &quot;facHigh&quot;: 0.0,
                &quot;maxSetBean&quot;: null,
                &quot;dtc&quot;: 5001,
                &quot;level&quot;: 6,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-24 15:12:13&quot;,
                &quot;children&quot;: null,
                &quot;treeName&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;treeID&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;parentID&quot;: &quot;LIST_BLE4BEQ0BW_3&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;statusText&quot;: &quot;max.status.normal&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:---------------|:-----|:------------|
| serialNum      | string| Device SN   |
| lost           | string| Device online status (0: online, 1: offline) |
| status         | int   | Device status (0: offline, 1: online, 2: standby, 3: fault, others: disconnected) |
| alias          | string| Alias       |
| location       | string| Address     |
| dataLogSn      | string| Data logger serial number |
| normalPower    | string| Rated power |
| eToday         | string| Today's generated power at the backend |
| eTotal         | string| Total generated power at the backend |
| lastUpdateTime | string| Last update time |
| tcpServerIp    | string| Server address |
| fwVersion      | string| Inverter firmware version |

**Remarks**

- The retrieval frequency is once every 5 minutes.


---

# 23. Max Latest Detailed Data

*Page ID: `11292919843180935`*

**Brief Description:**

- The data format and parameter description of the last detailed data of the Max device
- `Only applicable to: Batch retrieval of the last data of devices.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;max&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;time&quot;: &quot;2024-05-25 14:34:23&quot;,
                &quot;powerToday&quot;: 0.0,
                &quot;powerTotal&quot;: 0.0,
                &quot;ipmTemperature&quot;: 0.0,
                &quot;rac&quot;: 0.0,
                &quot;eRacToday&quot;: 0.0,
                &quot;eRacTotal&quot;: 0.0,
                &quot;strFault&quot;: 0,
                &quot;dwStringWarningValue1&quot;: 0,
                &quot;wStringStatusValue&quot;: 0,
                &quot;wPIDFaultValue&quot;: 0,
                &quot;serialNum&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;dataLogSn&quot;: &quot;BLE4BEQ0BW&quot;,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716618863392,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 2069.9,
                &quot;vpv1&quot;: 586.4,
                &quot;vpv2&quot;: 646.5,
                &quot;vpv3&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;vpv5&quot;: 0.0,
                &quot;vpv6&quot;: 0.0,
                &quot;vpv7&quot;: 0.0,
                &quot;vpv8&quot;: 0.0,
                &quot;ipv1&quot;: 0.7,
                &quot;ipv2&quot;: 2.4,
                &quot;ipv3&quot;: 0.0,
                &quot;ipv4&quot;: 0.0,
                &quot;ipv5&quot;: 0.0,
                &quot;ipv6&quot;: 0.0,
                &quot;ipv7&quot;: 0.0,
                &quot;ipv8&quot;: 0.0,
                &quot;ppv1&quot;: 410.4,
                &quot;ppv2&quot;: 1551.6,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;ppv5&quot;: 0.0,
                &quot;ppv6&quot;: 0.0,
                &quot;ppv7&quot;: 0.0,
                &quot;ppv8&quot;: 0.0,
                &quot;pac&quot;: 2038.9,
                &quot;fac&quot;: 49.98,
                &quot;vacr&quot;: 239.0,
                &quot;iacr&quot;: 3.1000001,
                &quot;pacr&quot;: 740.9,
                &quot;vacs&quot;: 234.1,
                &quot;iacs&quot;: 3.2,
                &quot;pacs&quot;: 749.1,
                &quot;vact&quot;: 237.0,
                &quot;iact&quot;: 3.3,
                &quot;pact&quot;: 782.1,
                &quot;vacRs&quot;: 414.30002,
                &quot;vacSt&quot;: 407.2,
                &quot;vacTr&quot;: 407.2,
                &quot;eacToday&quot;: 42.9,
                &quot;eacTotal&quot;: 115581.7,
                &quot;epvTotal&quot;: 115372.9,
                &quot;timeTotal&quot;: 4.4968542E7,
                &quot;epv1Today&quot;: 9.7,
                &quot;epv1Total&quot;: 27702.4,
                &quot;epv2Today&quot;: 32.9,
                &quot;epv2Total&quot;: 87670.5,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epv5Today&quot;: 0.0,
                &quot;epv5Total&quot;: 0.0,
                &quot;epv6Today&quot;: 0.0,
                &quot;epv6Total&quot;: 0.0,
                &quot;epv7Today&quot;: 0.0,
                &quot;epv7Total&quot;: 0.0,
                &quot;epv8Today&quot;: 0.0,
                &quot;epv8Total&quot;: 0.0,
                &quot;temperature&quot;: 52.5,
                &quot;temperature2&quot;: 41.4,
                &quot;temperature3&quot;: 39.100002,
                &quot;temperature4&quot;: 0.0,
                &quot;temperature5&quot;: 35.8,
                &quot;pBusVoltage&quot;: 332.6,
                &quot;nBusVoltage&quot;: 334.9,
                &quot;pf&quot;: 1.0,
                &quot;faultType&quot;: 0,
                &quot;faultCode1&quot;: 0,
                &quot;faultCode2&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 27500.0,
                &quot;deratingMode&quot;: 0,
                &quot;vPidPvape&quot;: 0.0,
                &quot;vPidPvbpe&quot;: 0.0,
                &quot;vPidPvcpe&quot;: 0.0,
                &quot;vPidPvdpe&quot;: 0.0,
                &quot;vPidPvepe&quot;: 0.0,
                &quot;vPidPvfpe&quot;: 0.0,
                &quot;vPidPvgpe&quot;: 0.0,
                &quot;vPidPvhpe&quot;: 0.0,
                &quot;iPidPvape&quot;: 0.0,
                &quot;iPidPvbpe&quot;: 0.0,
                &quot;iPidPvcpe&quot;: 0.0,
                &quot;iPidPvdpe&quot;: 0.0,
                &quot;iPidPvepe&quot;: 0.0,
                &quot;iPidPvfpe&quot;: 0.0,
                &quot;iPidPvgpe&quot;: 0.0,
                &quot;iPidPvhpe&quot;: 0.0,
                &quot;pidStatus&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;vString9&quot;: 0.0,
                &quot;currentString9&quot;: 0.0,
                &quot;vString10&quot;: 0.0,
                &quot;currentString10&quot;: 0.0,
                &quot;vString11&quot;: 0.0,
                &quot;currentString11&quot;: 0.0,
                &quot;vString12&quot;: 0.0,
                &quot;currentString12&quot;: 0.0,
                &quot;vString13&quot;: 0.0,
                &quot;currentString13&quot;: 0.0,
                &quot;vString14&quot;: 0.0,
                &quot;currentString14&quot;: 0.0,
                &quot;vString15&quot;: 0.0,
                &quot;currentString15&quot;: 0.0,
                &quot;vString16&quot;: 0.0,
                &quot;currentString16&quot;: 0.0,
                &quot;warningValue1&quot;: 0,
                &quot;warningValue2&quot;: 0,
                &quot;warningValue3&quot;: 0,
                &quot;faultValue&quot;: 0,
                &quot;pidFaultCode&quot;: 0,
                &quot;pvIso&quot;: 3004,
                &quot;rDci&quot;: 0.2,
                &quot;sDci&quot;: 0.7,
                &quot;tDci&quot;: 6552.7,
                &quot;pidBus&quot;: 0.0,
                &quot;gfci&quot;: 166,
                &quot;apfStatus&quot;: 0,
                &quot;ctir&quot;: 0.0,
                &quot;ctis&quot;: 0.0,
                &quot;ctit&quot;: 0.0,
                &quot;ctqr&quot;: 0.0,
                &quot;ctqs&quot;: 0.0,
                &quot;ctqt&quot;: 0.0,
                &quot;ctharir&quot;: 0.0,
                &quot;ctharis&quot;: 0.0,
                &quot;ctharit&quot;: 0.0,
                &quot;compqr&quot;: 0.0,
                &quot;compqs&quot;: 0.0,
                &quot;compqt&quot;: 0.0,
                &quot;compharir&quot;: 0.0,
                &quot;compharis&quot;: 0.0,
                &quot;compharit&quot;: 0.0,
                &quot;reactPower&quot;: 0.0,
                &quot;reactPowerMax&quot;: 0.0,
                &quot;reactPowerTotal&quot;: 0.0,
                &quot;debug1&quot;: &quot;0，0，0，0，0，9988，0，27500&quot;,
                &quot;debug2&quot;: &quot;0，24，5，24，24，5，25，0&quot;,
                &quot;debug3&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;vpv9&quot;: 0.0,
                &quot;vpv10&quot;: 0.0,
                &quot;vpv11&quot;: 0.0,
                &quot;vpv12&quot;: 0.0,
                &quot;vpv13&quot;: 0.0,
                &quot;vpv14&quot;: 0.0,
                &quot;vpv15&quot;: 0.0,
                &quot;vpv16&quot;: 0.0,
                &quot;ipv9&quot;: 0.0,
                &quot;ipv10&quot;: 0.0,
                &quot;ipv11&quot;: 0.0,
                &quot;ipv12&quot;: 0.0,
                &quot;ipv13&quot;: 0.0,
                &quot;ipv14&quot;: 0.0,
                &quot;ipv15&quot;: 0.0,
                &quot;ipv16&quot;: 0.0,
                &quot;ppv9&quot;: 0.0,
                &quot;ppv10&quot;: 0.0,
                &quot;ppv11&quot;: 0.0,
                &quot;ppv12&quot;: 0.0,
                &quot;ppv13&quot;: 0.0,
                &quot;ppv14&quot;: 0.0,
                &quot;ppv15&quot;: 0.0,
                &quot;ppv16&quot;: 0.0,
                &quot;vString17&quot;: 0.0,
                &quot;vString18&quot;: 0.0,
                &quot;vString19&quot;: 0.0,
                &quot;vString20&quot;: 0.0,
                &quot;vString21&quot;: 0.0,
                &quot;vString22&quot;: 0.0,
                &quot;vString23&quot;: 0.0,
                &quot;vString24&quot;: 0.0,
                &quot;vString25&quot;: 0.0,
                &quot;vString26&quot;: 0.0,
                &quot;vString27&quot;: 0.0,
                &quot;vString28&quot;: 0.0,
                &quot;vString29&quot;: 0.0,
                &quot;vString30&quot;: 0.0,
                &quot;vString31&quot;: 0.0,
                &quot;vString32&quot;: 0.0,
                &quot;currentString17&quot;: 0.0,
                &quot;currentString18&quot;: 0.0,
                &quot;currentString19&quot;: 0.0,
                &quot;currentString20&quot;: 0.0,
                &quot;currentString21&quot;: 0.0,
                &quot;currentString22&quot;: 0.0,
                &quot;currentString23&quot;: 0.0,
                &quot;currentString24&quot;: 0.0,
                &quot;currentString25&quot;: 0.0,
                &quot;currentString26&quot;: 0.0,
                &quot;currentString27&quot;: 0.0,
                &quot;currentString28&quot;: 0.0,
                &quot;currentString29&quot;: 0.0,
                &quot;currentString30&quot;: 0.0,
                &quot;currentString31&quot;: 0.0,
                &quot;currentString32&quot;: 0.0,
                &quot;vPidPvpe9&quot;: 0.0,
                &quot;vPidPvpe10&quot;: 0.0,
                &quot;vPidPvpe11&quot;: 0.0,
                &quot;vPidPvpe12&quot;: 0.0,
                &quot;vPidPvpe13&quot;: 0.0,
                &quot;vPidPvpe14&quot;: 0.0,
                &quot;vPidPvpe15&quot;: 0.0,
                &quot;vPidPvpe16&quot;: 0.0,
                &quot;iPidPvpe9&quot;: 0.0,
                &quot;iPidPvpe10&quot;: 0.0,
                &quot;iPidPvpe11&quot;: 0.0,
                &quot;iPidPvpe12&quot;: 0.0,
                &quot;iPidPvpe13&quot;: 0.0,
                &quot;iPidPvpe14&quot;: 0.0,
                &quot;iPidPvpe15&quot;: 0.0,
                &quot;iPidPvpe16&quot;: 0.0,
                &quot;epv9Today&quot;: 0.0,
                &quot;epv9Total&quot;: 0.0,
                &quot;epv10Today&quot;: 0.0,
                &quot;epv10Total&quot;: 0.0,
                &quot;epv11Today&quot;: 0.0,
                &quot;epv11Total&quot;: 0.0,
                &quot;epv12Today&quot;: 0.0,
                &quot;epv12Total&quot;: 0.0,
                &quot;epv13Today&quot;: 0.0,
                &quot;epv13Total&quot;: 0.0,
                &quot;epv14Today&quot;: 0.0,
                &quot;epv14Total&quot;: 0.0,
                &quot;epv15Today&quot;: 0.0,
                &quot;epv15Total&quot;: 0.0,
                &quot;epv16Today&quot;: 0.0,
                &quot;epv16Total&quot;: 0.0,
                &quot;maxBean&quot;: null,
                &quot;afciStatus&quot;: 0,
                &quot;afciPv1&quot;: 0,
                &quot;afciPv2&quot;: 0,
                &quot;again&quot;: false,
                &quot;warnBit&quot;: 0,
                &quot;timeCalendar&quot;: 1716618863392,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;strUnmatch&quot;: 0,
                &quot;strUnblance&quot;: 0,
                &quot;strBreak&quot;: 0,
                &quot;pidStatusText&quot;: &quot;Lost&quot;,
                &quot;apfStatusText&quot;: &quot;None&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameters Description**

| Parameter Name | Type   | Description                        |
|:---------------|:-------|------------------------------------|
| serialNum         | int    | Max device SN                      |
| status         | string | Max status (0: Standby, 1: , 2: Discharge, 3: Fault, 4: Flash) |
| isAgain        | string | Whether it is a retransmission (0: Not retransmission, 1: Retransmission) |
| calendar       | int    | Time (Calendar)                    |
| day            | int    | Time - Day                         |
| ppv            | string | Total PV input power (W)           |
| vpv1           | string | PV1 voltage (V)                    |
| vpv2           | string | PV2 voltage (V)                    |
| vpv3           | string | PV3 voltage (V)                    |
| vpv4           | string | PV4 voltage (V)                    |
| vpv5           | string | PV5 voltage (V)                    |
| vpv6           | string | PV6 voltage (V)                    |
| vpv7           | string | PV7 voltage (V)                    |
| vpv8           | string | PV8 voltage (V)                    |
| ipv1           | string | PV1 current (A)                    |
| ipv2           | string | PV2 current (A)                    |
| ipv3           | string | PV3 current (A)                    |
| ipv4           | string | PV4 current (A)                    |
| ipv5           | string | PV5 current (A)                    |
| ipv6           | string | PV6 current (A)                    |
| ipv7           | string | PV7 current (A)                    |
| ipv8           | string | PV8 current (A)                    |
| PPV1           | string | PV1 power (W)                      |
| PPV2           | string | PV2 power (W)                      |
| PPV3           | string | PV3 power (W)                      |
| PPV4           | string | PV4 power (W)                      |
| PPV5           | string | PV5 power (W)                      |
| PPV6           | string | PV6 power (W)                      |
| PPV7           | string | PV7 power (W)                      |
| PPV8           | string | PV8 power (W)                      |
| PPV9           | string | PV9 power (W)                      |
| PPV10          | string | PV10 power (W)                     |
| PPV11          | string | PV11 power (W)                     |
| PPV12          | string | PV12 power (W)                     |
| PPV13          | string | PV13 power (W)                     |
| PPV14          | string | PV14 power (W)                     |
| PPV15          | string | PV15 power (W)                     |
| PPV16          | string | PV16 power (W)                     |
| pac            | string | Output power (W)                   |
| fac            | string | Grid frequency                     |
| vacr           | string | R-phase voltage (V)                |
| vacs           | string | S-phase voltage (V)                |
| vact           | string | T-phase voltage (V)                |
| iacr           | string | R-phase current (A)                |
| iacs           | string | S-phase current (A)                |
| iact           | string | T-phase current (A)                |
| pacr           | string | R-phase output power (W)           |
| pacs           | string | S-phase output power (W)           |
| pact           | string | T-phase output power (W)           |
| vacRs          | string | RS line voltage (V)                |
| vacSt          | string | ST line voltage (V)                |
| vacTr          | string | TR line voltage (V)                |
| vPidPvape      | string | pid voltage 1 (V)                  |
| vPidPvbpe      | string | pid voltage 2 (V)                  |
| vPidPvcpe      | string | pid voltage 3 (V)                  |
| vPidPvdpe      | string | pid voltage 4 (V)                  |
| vPidPvepe      | string | pid voltage 5 (V)                  |
| vPidPvfpe      | string | pid voltage 6 (V)                  |
| vPidPvgpe      | string | pid voltage 7 (V)                  |
| vPidPvhpe      | string | pid voltage 8 (V)                  |
| ipidPvape      | string | pid current 1 (A)                  |
| ipidPvbpe      | string | pid current 2 (A)                  |
| ipidPvcpe      | string | pid current 3 (A)                  |
| ipidPvdpe      | string | pid current 4 (A)                  |
| ipidPvepe      | string | pid current 5 (A)                  |
| ipidPvfpe      | string | pid current 6 (A)                  |
| ipidPvgpe      | string | pid current 7 (A)                  |
| ipidPvhpe      | string | pid current 8 (A)                  |
| vString1       | string | String voltage 1                   |
| vString2       | string | String voltage 2                   |
| vString3       | string | String voltage 3                   |
| vString4       | string | String voltage 4                   |
| vString5       | string | String voltage 5                   |
| vString6       | string | String voltage 6                   |
| vString7       | string | String voltage 7                   |
| vString8       | string | String voltage 8                   |
| vString9       | string | String voltage 9                   |
| vString10      | string | String voltage 10                  |
| vString11      | string | String voltage 11                  |
| vString12      | string | String voltage 12                  |
| vString13      | string | String voltage 13                  |
| vString14      | string | String voltage 14                  |
| vString15      | string | String voltage 15                  |
| vString16      | string | String voltage 16                  |
| vString17      | string | String voltage 17                  |
| vString18      | string | String voltage 18                  |
| vString19      | string | String voltage 19                  |
| vString20      | string | String voltage 20                  |
| vString21      | string | String voltage 21                  |
| vString22      | string | String voltage 22                  |
| vString23      | string | String voltage 23                  |
| vString24      | string | String voltage 24                  |
| vString25      | string | String voltage 25                  |
| vString26      | string | String voltage 26                  |
| vString27      | string | String voltage 27                  |
| vString28      | string | String voltage 28                  |
| vString29      | string | String voltage 29                  |
| vString30      | string | String voltage 30                  |
| vString31      | string | String voltage 31                  |
| vString32      | string | String voltage 32                  |
| currentString1 | string | String current 1                   |
| currentString2 | string | String current 2                   |
| currentString3 | string | String current 3                   |
| currentString4 | string | String current 4                   |
| currentString5 | string | String current 5                   |
| currentString6 | string | String current 6                   |
| currentString7 | string | String current 7                   |
| currentString8 | string | String current 8                   |
| currentString9 | string | String current 9                   |
| currentString10| string | String current 10                  |
| currentString11| string | String current 11                  |
| currentString12| string | String current 12                  |
| currentString13| string | String current 13                  |
| currentString14| string | String current 14                  |
| currentString15| string | String current 15                  |
| currentString16| string | String current 16                  |
| currentString17| string | String current 17                  |
| currentString18| string | String current 18                  |
| currentString19| string | String current 19                  |
| currentString20| string | String current 20                  |
| currentString21| string | String current 21                  |
| currentString22| string | String current 22                  |
| currentString23| string | String current 23                  |
| currentString24| string | String current 24                  |
| currentString25| string | String current 25                  |
| currentString26| string | String current 26                  |
| currentString27| string | String current 27                  |
| currentString28| string | String current 28                  |
| currentString29| string | String current 29                  |
| currentString30| string | String current 30                  |
| currentString31| string | String current 31                  |
| currentString32| string | String current 32                  |
| faultValue     | string | Fault value                        |
| WarnBit        | string | Fault bit                          |
| warningValue1  | string | Warning value 1                    |
| warningValue2  | string | Warning value 2                    |
| warningValue3  | string | Warning value 3                    |
| pidFaultCode   | string | pid fault code                     |
| StrUnmatch     | string | String mismatch                    |
| StrUnblance    | string | String current imbalance           |
| StrBreak       | string | String not connected               |
| pvIso          | string | Insulation resistance              |
| rDci           | string | R-phase DC component               |
| sDci           | string | S-phase DC component               |
| tDci           | string | T-phase DC component               |
| pidBus         | string | PID BUS voltage                    |
| gfci           | string | Leakage current                    |
| apfStatus      | string | apf/svg status                     |
| ctir           | string | R-phase CT side current            |
| ctis           | string | S-phase CT side current            |
| ctit           | string | T-phase CT side current            |
| ctqr           | string | R-phase CT side reactive power     |
| ctqs           | string | S-phase CT side reactive power     |
| ctqt           | string | T-phase CT side power              |
| ctharir        | string | R-phase CT side harmonic amount    |
| ctharis        | string | S-phase CT side harmonic amount    |
| ctharit        | string | T-phase CT side harmonic amount    |
| compqr         | string | R-phase compensation reactive power|
| compqs         | string | S-phase compensation reactive power|
| compqt         | string | T-phase compensation reactive power|
| compharir      | string | R-phase compensation harmonic amount|
| compharis      | string | S-phase compensation harmonic amount|
| compharit      | string | T-phase compensation harmonic amount|
| pidStatus      | string | pid status                         |
| faultType      | string | Fault code                         |
| faultCode1     | string | Fault code                         |
| faultCode2     | string | Fault code                         |
| warnCode       | string | Warning code                       |
| opFullwatt     | string | Output power limit                 |
| deratingMode   | string | Derating mode                      |
| pf             | string | pf value                           |
| pBusVoltage    | string | P Bus voltage                      |
| nBusVoltage    | string | N Bus voltage                      |
| temperature1   | string | AMTemp1 (℃)                        |
| temperature2   | string | INVTemp (℃)                        |
| temperature3   | string | BTTemp (℃)                         |
| temperature4   | string | OUTTemp (℃)                        |
| temperature5   | string | AMTemp2 (℃)                        |
| ipmTemperature | string | IPM temperature                    |
| rac            | string | Reactive power Var                 |
| eRacToday      | string | Reactive energy today kVarh        |
| eRacTotal      | string | Total reactive energy kVarh        |
| strFault       | string | String error                       |
| dwStringWarningValue1 | string |                              |
| wStringStatusValue | string |                                 |
| wPIDFaultValue | string |                                     |
| epv1Today      | string | PV1 energy generated today         |
| epv1Total      | string | Total PV1 energy generated         |
| epv2Today      | string | PV2 energy generated today         |
| epv2Total      | string | Total PV2 energy generated         |
| epv3Today      | string | PV3 energy generated today         |
| epv3Total      | string | Total PV3 energy generated         |
| epv4Today      | string | PV4 energy generated today         |
| epv4Total      | string | Total PV4 energy generated         |
| epv5Today      | string | PV5 energy generated today         |
| epv5Total      | string | Total PV5 energy generated         |
| epv6Today      | string | PV6 energy generated today         |
| epv6Total      | string | Total PV6 energy generated         |
| epv7Today      | string | PV7 energy generated today         |
| epv7Total      | string | Total PV7 energy generated         |
| epv8Today      | string | PV8 energy generated today         |
| epv8Total      | string | Total PV8 energy generated         |
| eacToday       | string | Energy generated today             |
| eacTotal       | string | Total energy generated             |
| epvTotal       | string | Total PV energy generated          |
| timeTotal      | string | Total run time                     |

**Notes**

- The acquisition frequency is once every 5 minutes.


---

# 24. Max Device Historical Data

*Page ID: `11292920771207078`*

**Brief Description:**

- Data format and parameter description of max device historical data
- `Only applicable: to retrieve all detailed data of a specific device for a specific day.`

**Return Example**

``` 
{
     &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-24&quot;,
        &quot;datas&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;time&quot;: &quot;2024-05-25 14:44:23&quot;,
                &quot;powerToday&quot;: 0.0,
                &quot;powerTotal&quot;: 0.0,
                &quot;ipmTemperature&quot;: 0.0,
                &quot;rac&quot;: 0.0,
                &quot;eRacToday&quot;: 0.0,
                &quot;eRacTotal&quot;: 0.0,
                &quot;strFault&quot;: 0,
                &quot;dwStringWarningValue1&quot;: 0,
                &quot;wStringStatusValue&quot;: 0,
                &quot;wPIDFaultValue&quot;: 0,
                &quot;serialNum&quot;: &quot;HPJ0BF20FU&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716619463000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 2086.0,
                &quot;vpv1&quot;: 612.3,
                &quot;vpv2&quot;: 637.8,
                &quot;vpv3&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;vpv5&quot;: 0.0,
                &quot;vpv6&quot;: 0.0,
                &quot;vpv7&quot;: 0.0,
                &quot;vpv8&quot;: 0.0,
                &quot;ipv1&quot;: 0.7,
                &quot;ipv2&quot;: 2.5,
                &quot;ipv3&quot;: 0.0,
                &quot;ipv4&quot;: 0.0,
                &quot;ipv5&quot;: 0.0,
                &quot;ipv6&quot;: 0.0,
                &quot;ipv7&quot;: 0.0,
                &quot;ipv8&quot;: 0.0,
                &quot;ppv1&quot;: 428.6,
                &quot;ppv2&quot;: 1594.5,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;ppv5&quot;: 0.0,
                &quot;ppv6&quot;: 0.0,
                &quot;ppv7&quot;: 0.0,
                &quot;ppv8&quot;: 0.0,
                &quot;pac&quot;: 2054.8,
                &quot;fac&quot;: 49.97,
                &quot;vacr&quot;: 237.5,
                &quot;iacr&quot;: 3.2,
                &quot;pacr&quot;: 760.0,
                &quot;vacs&quot;: 236.3,
                &quot;iacs&quot;: 3.2,
                &quot;pacs&quot;: 756.1,
                &quot;vact&quot;: 236.1,
                &quot;iact&quot;: 3.3,
                &quot;pact&quot;: 779.1,
                &quot;vacRs&quot;: 413.8,
                &quot;vacSt&quot;: 408.9,
                &quot;vacTr&quot;: 405.5,
                &quot;eacToday&quot;: 43.2,
                &quot;eacTotal&quot;: 115582.0,
                &quot;epvTotal&quot;: 115373.2,
                &quot;timeTotal&quot;: 4.4969139E7,
                &quot;epv1Today&quot;: 9.8,
                &quot;epv1Total&quot;: 27702.5,
                &quot;epv2Today&quot;: 33.1,
                &quot;epv2Total&quot;: 87670.7,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epv5Today&quot;: 0.0,
                &quot;epv5Total&quot;: 0.0,
                &quot;epv6Today&quot;: 0.0,
                &quot;epv6Total&quot;: 0.0,
                &quot;epv7Today&quot;: 0.0,
                &quot;epv7Total&quot;: 0.0,
                &quot;epv8Today&quot;: 0.0,
                &quot;epv8Total&quot;: 0.0,
                &quot;temperature&quot;: 52.8,
                &quot;temperature2&quot;: 41.9,
                &quot;temperature3&quot;: 39.4,
                &quot;temperature4&quot;: 0.0,
                &quot;temperature5&quot;: 36.0,
                &quot;pBusVoltage&quot;: 327.9,
                &quot;nBusVoltage&quot;: 330.6,
                &quot;pf&quot;: 1.0,
                &quot;faultType&quot;: 0,
                &quot;faultCode1&quot;: 0,
                &quot;faultCode2&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 27500.0,
                &quot;deratingMode&quot;: 0,
                &quot;vPidPvape&quot;: 0.0,
                &quot;vPidPvbpe&quot;: 0.0,
                &quot;vPidPvcpe&quot;: 0.0,
                &quot;vPidPvdpe&quot;: 0.0,
                &quot;vPidPvepe&quot;: 0.0,
                &quot;vPidPvfpe&quot;: 0.0,
                &quot;vPidPvgpe&quot;: 0.0,
                &quot;vPidPvhpe&quot;: 0.0,
                &quot;iPidPvape&quot;: 0.0,
                &quot;iPidPvbpe&quot;: 0.0,
                &quot;iPidPvcpe&quot;: 0.0,
                &quot;iPidPvdpe&quot;: 0.0,
                &quot;iPidPvepe&quot;: 0.0,
                &quot;iPidPvfpe&quot;: 0.0,
                &quot;iPidPvgpe&quot;: 0.0,
                &quot;iPidPvhpe&quot;: 0.0,
                &quot;pidStatus&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;vString9&quot;: 0.0,
                &quot;currentString9&quot;: 0.0,
                &quot;vString10&quot;: 0.0,
                &quot;currentString10&quot;: 0.0,
                &quot;vString11&quot;: 0.0,
                &quot;currentString11&quot;: 0.0,
                &quot;vString12&quot;: 0.0,
                &quot;currentString12&quot;: 0.0,
                &quot;vString13&quot;: 0.0,
                &quot;currentString13&quot;: 0.0,
                &quot;vString14&quot;: 0.0,
                &quot;currentString14&quot;: 0.0,
                &quot;vString15&quot;: 0.0,
                &quot;currentString15&quot;: 0.0,
                &quot;vString16&quot;: 0.0,
                &quot;currentString16&quot;: 0.0,
                &quot;warningValue1&quot;: 0,
                &quot;warningValue2&quot;: 0,
                &quot;warningValue3&quot;: 0,
                &quot;faultValue&quot;: 0,
                &quot;pidFaultCode&quot;: 0,
                &quot;pvIso&quot;: 3004,
                &quot;rDci&quot;: 0.0,
                &quot;sDci&quot;: 0.5,
                &quot;tDci&quot;: 6553.1,
                &quot;pidBus&quot;: 0.0,
                &quot;gfci&quot;: 166,
                &quot;apfStatus&quot;: 0,
                &quot;ctir&quot;: 0.0,
                &quot;ctis&quot;: 0.0,
                &quot;ctit&quot;: 0.0,
                &quot;ctqr&quot;: 0.0,
                &quot;ctqs&quot;: 0.0,
                &quot;ctqt&quot;: 0.0,
                &quot;ctharir&quot;: 0.0,
                &quot;ctharis&quot;: 0.0,
                &quot;ctharit&quot;: 0.0,
                &quot;compqr&quot;: 0.0,
                &quot;compqs&quot;: 0.0,
                &quot;compqt&quot;: 0.0,
                &quot;compharir&quot;: 0.0,
                &quot;compharis&quot;: 0.0,
                &quot;compharit&quot;: 0.0,
                &quot;reactPower&quot;: 0.0,
                &quot;reactPowerMax&quot;: 0.0,
                &quot;reactPowerTotal&quot;: 0.0,
                &quot;debug1&quot;: &quot;0，0，0，0，0，10001，0，27500&quot;,
                &quot;debug2&quot;: &quot;0，24，5，24，24，5，25，0&quot;,
                &quot;debug3&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;vpv9&quot;: 0.0,
                &quot;vpv10&quot;: 0.0,
                &quot;vpv11&quot;: 0.0,
                &quot;vpv12&quot;: 0.0,
                &quot;vpv13&quot;: 0.0,
                &quot;vpv14&quot;: 0.0,
                &quot;vpv15&quot;: 0.0,
                &quot;vpv16&quot;: 0.0,
                &quot;ipv9&quot;: 0.0,
                &quot;ipv10&quot;: 0.0,
                &quot;ipv11&quot;: 0.0,
                &quot;ipv12&quot;: 0.0,
                &quot;ipv13&quot;: 0.0,
                &quot;ipv14&quot;: 0.0,
                &quot;ipv15&quot;: 0.0,
                &quot;ipv16&quot;: 0.0,
                &quot;ppv9&quot;: 0.0,
                &quot;ppv10&quot;: 0.0,
                &quot;ppv11&quot;: 0.0,
                &quot;ppv12&quot;: 0.0,
                &quot;ppv13&quot;: 0.0,
                &quot;ppv14&quot;: 0.0,
                &quot;ppv15&quot;: 0.0,
                &quot;ppv16&quot;: 0.0,
                &quot;vString17&quot;: 0.0,
                &quot;vString18&quot;: 0.0,
                &quot;vString19&quot;: 0.0,
                &quot;vString20&quot;: 0.0,
                &quot;vString21&quot;: 0.0,
                &quot;vString22&quot;: 0.0,
                &quot;vString23&quot;: 0.0,
                &quot;vString24&quot;: 0.0,
                &quot;vString25&quot;: 0.0,
                &quot;vString26&quot;: 0.0,
                &quot;vString27&quot;: 0.0,
                &quot;vString28&quot;: 0.0,
                &quot;vString29&quot;: 0.0,
                &quot;vString30&quot;: 0.0,
                &quot;vString31&quot;: 0.0,
                &quot;vString32&quot;: 0.0,
                &quot;currentString17&quot;: 0.0,
                &quot;currentString18&quot;: 0.0,
                &quot;currentString19&quot;: 0.0,
                &quot;currentString20&quot;: 0.0,
                &quot;currentString21&quot;: 0.0,
                &quot;currentString22&quot;: 0.0,
                &quot;currentString23&quot;: 0.0,
                &quot;currentString24&quot;: 0.0,
                &quot;currentString25&quot;: 0.0,
                &quot;currentString26&quot;: 0.0,
                &quot;currentString27&quot;: 0.0,
                &quot;currentString28&quot;: 0.0,
                &quot;currentString29&quot;: 0.0,
                &quot;currentString30&quot;: 0.0,
                &quot;currentString31&quot;: 0.0,
                &quot;currentString32&quot;: 0.0,
                &quot;vPidPvpe9&quot;: 0.0,
                &quot;vPidPvpe10&quot;: 0.0,
                &quot;vPidPvpe11&quot;: 0.0,
                &quot;vPidPvpe12&quot;: 0.0,
                &quot;vPidPvpe13&quot;: 0.0,
                &quot;vPidPvpe14&quot;: 0.0,
                &quot;vPidPvpe15&quot;: 0.0,
                &quot;vPidPvpe16&quot;: 0.0,
                &quot;iPidPvpe9&quot;: 0.0,
                &quot;iPidPvpe10&quot;: 0.0,
                &quot;iPidPvpe11&quot;: 0.0,
                &quot;iPidPvpe12&quot;: 0.0,
                &quot;iPidPvpe13&quot;: 0.0,
                &quot;iPidPvpe14&quot;: 0.0,
                &quot;iPidPvpe15&quot;: 0.0,
                &quot;iPidPvpe16&quot;: 0.0,
                &quot;epv9Today&quot;: 0.0,
                &quot;epv9Total&quot;: 0.0,
                &quot;epv10Today&quot;: 0.0,
                &quot;epv10Total&quot;: 0.0,
                &quot;epv11Today&quot;: 0.0,
                &quot;epv11Total&quot;: 0.0,
                &quot;epv12Today&quot;: 0.0,
                &quot;epv12Total&quot;: 0.0,
                &quot;epv13Today&quot;: 0.0,
                &quot;epv13Total&quot;: 0.0,
                &quot;epv14Today&quot;: 0.0,
                &quot;epv14Total&quot;: 0.0,
                &quot;epv15Today&quot;: 0.0,
                &quot;epv15Total&quot;: 0.0,
                &quot;epv16Today&quot;: 0.0,
                &quot;epv16Total&quot;: 0.0,
                &quot;maxBean&quot;: null,
                &quot;afciStatus&quot;: 0,
                &quot;afciPv1&quot;: 0,
                &quot;afciPv2&quot;: 0,
                &quot;again&quot;: false,
                &quot;warnBit&quot;: 0,
                &quot;timeCalendar&quot;: 1716619463000,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;strUnmatch&quot;: 0,
                &quot;strUnblance&quot;: 0,
                &quot;strBreak&quot;: 0,
                &quot;pidStatusText&quot;: &quot;Lost&quot;,
                &quot;apfStatusText&quot;: &quot;None&quot;
            }
],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name            | Type   | Description                                 |
|:--------------------------|:-------|:--------------------------------------------|
| serialNum                    | string | Max device SN                               |
| status                    | string | Max status (0: Standby, 1:, 2: Discharge, 3: Fault, 4: Flash) |
| isAgain                   | string | Whether it is a retransmission (0: No, 1: Yes) |
| calendar                  | time   | Time (Calendar)                             |
| day                       | time   | Time - Day                                  |
| ppv                       | string | Total PV input power (W)                    |
| vpv1                      | string | PV1 voltage (V)                             |
| vpv2                      | string | PV2 voltage (V)                             |
| vpv3                      | string | PV3 voltage (V)                             |
| vpv4                      | string | PV4 voltage (V)                             |
| vpv5                      | string | PV5 voltage (V)                             |
| vpv6                      | string | PV6 voltage (V)                             |
| vpv7                      | string | PV7 voltage (V)                             |
| vpv8                      | string | PV8 voltage (V)                             |
| ipv1                      | string | PV1 current (A)                             |
| ipv2                      | string | PV2 current (A)                             |
| ipv3                      | string | PV3 current (A)                             |
| ipv4                      | string | PV4 current (A)                             |
| ipv5                      | string | PV5 current (A)                             |
| ipv6                      | string | PV6 current (A)                             |
| ipv7                      | string | PV7 current (A)                             |
| ipv8                      | string | PV8 current (A)                             |
| PPV1                      | string | PV1 power (W)                               |
| PPV2                      | string | PV2 power (W)                               |
| PPV3                      | string | PV3 power (W)                               |
| PPV4                      | string | PV4 power (W)                               |
| PPV5                      | string | PV5 power (W)                               |
| PPV6                      | string | PV6 power (W)                               |
| PPV7                      | string | PV7 power (W)                               |
| PPV8                      | string | PV8 power (W)                               |
| pac                       | string | Output power (W)                            |
| fac                       | string | Grid frequency                              |
| vacr                      | string | R phase voltage (V)                         |
| vacs                      | string | S phase voltage (V)                         |
| vact                      | string | T phase voltage (V)                         |
| iacr                      | string | R phase current (A)                         |
| iacs                      | string | S phase current (A)                         |
| iact                      | string | T phase current (A)                         |
| pacr                      | string | R phase output power (W)                    |
| pacs                      | string | S phase output power (W)                    |
| pact                      | string | T phase output power (W)                    |
| vacRs                     | string | RS line voltage (V)                         |
| vacSt                     | string | ST line voltage (V)                         |
| vacTr                     | string | TR line voltage (V)                         |
| vPidPvape                 | string | PID voltage 1 (V)                           |
| vPidPvbpe                 | string | PID voltage 2 (V)                           |
| vPidPvcpe                 | string | PID voltage 3 (V)                           |
| vPidPvdpe                 | string | PID voltage 4 (V)                           |
| vPidPvepe                 | string | PID voltage 5 (V)                           |
| vPidPvfpe                 | string | PID voltage 6 (V)                           |
| vPidPvgpe                 | string | PID voltage 7 (V)                           |
| vPidPvhpe                 | string | PID voltage 8 (V)                           |
| ipidPvape                 | string | PID current 1 (A)                           |
| ipidPvbpe                 | string | PID current 2 (A)                           |
| ipidPvcpe                 | string | PID current 3 (A)                           |
| ipidPvdpe                 | string | PID current 4 (A)                           |
| ipidPvepe                 | string | PID current 5 (A)                           |
| ipidPvfpe                 | string | PID current 6 (A)                           |
| ipidPvgpe                 | string | PID current 7 (A)                           |
| ipidPvhpe                 | string | PID current 8 (A)                           |
| vString1                  | string | String voltage 1                            |
| vString2                  | string | String voltage 2                            |
| vString3                  | string | String voltage 3                            |
| vString4                  | string | String voltage 4                            |
| vString5                  | string | String voltage 5                            |
| vString6                  | string | String voltage 6                            |
| vString7                  | string | String voltage 7                            |
| vString8                  | string | String voltage 8                            |
| vString9                  | string | String voltage 9                            |
| vString10                 | string | String voltage 10                           |
| vString11                 | string | String voltage 11                           |
| vString12                 | string | String voltage 12                           |
| vString13                 | string | String voltage 13                           |
| vString14                 | string | String voltage 14                           |
| vString15                 | string | String voltage 15                           |
| vString16                 | string | String voltage 16                           |
| vString17                 | string | String voltage 17                           |
| vString18                 | string | String voltage 18                           |
| vString19                 | string | String voltage 19                           |
| vString20                 | string | String voltage 20                           |
| vString21                 | string | String voltage 21                           |
| vString22                 | string | String voltage 22                           |
| vString23                 | string | String voltage 23                           |
| vString24                 | string | String voltage 24                           |
| vString25                 | string | String voltage 25                           |
| vString26                 | string | String voltage 26                           |
| vString27                 | string | String voltage 27                           |
| vString28                 | string | String voltage 28                           |
| vString29                 | string | String voltage 29                           |
| vString30                 | string | String voltage 30                           |
| vString31                 | string | String voltage 31                           |
| vString32                 | string | String voltage 32                           |
| currentString1            | string | String current 1                            |
| currentString2            | string | String current 2                            |
| currentString3            | string | String current 3                            |
| currentString4            | string | String current 4                            |
| currentString5            | string | String current 5                            |
| currentString6            | string | String current 6                            |
| currentString7            | string | String current 7                            |
| currentString8            | string | String current 8                            |
| currentString9            | string | String current 9                            |
| currentString10           | string | String current 10                           |
| currentString11           | string | String current 11                           |
| currentString12           | string | String current 12                           |
| currentString13           | string | String current 13                           |
| currentString14           | string | String current 14                           |
| currentString15           | string | String current 15                           |
| currentString16           | string | String current 16                           |
| currentString17           | string | String current 17                           |
| currentString18           | string | String current 18                           |
| currentString19           | string | String current 19                           |
| currentString20           | string | String current 20                           |
| currentString21           | string | String current 21                           |
| currentString22           | string | String current 22                           |
| currentString23           | string | String current 23                           |
| currentString24           | string | String current 24                           |
| currentString25           | string | String current 25                           |
| currentString26           | string | String current 26                           |
| currentString27           | string | String current 27                           |
| currentString28           | string | String current 28                           |
| currentString29           | string | String current 29                           |
| currentString30           | string | String current 30                           |
| currentString31           | string | String current 31                           |
| currentString32           | string | String current 32                           |
| faultValue                | string | Fault value                                 |
| WarnBit                   | string | Fault bit                                   |
| warningValue1             | string | Warning value 1                             |
| warningValue2             | string | Warning value 2                             |
| warningValue3             | string | Warning value 3                             |
| pidFaultCode              | string | PID fault code                              |
| StrUnmatch                | string | String mismatch                             |
| StrUnblance               | string | String current imbalance                    |
| StrBreak                  | string | String not connected                        |
| pvIso                     | string | Insulation resistance                       |
| rDci                      | string | R phase DC component                        |
| sDci                      | string | S phase DC component                        |
| tDci                      | string | T phase DC component                        |
| pidBus                    | string | PID BUS voltage                             |
| gfci                      | string | Leakage current                             |
| apfStatus                 | string | APF/SVG status                              |
| ctir                      | string | R phase CT side current                     |
| ctis                      | string | S phase CT side current                     |
| ctit                      | string | T phase CT side current                     |
| ctqr                      | string | R phase CT side reactive power              |
| ctqs                      | string | S phase CT side reactive power              |
| ctqt                      | string | T phase CT side reactive power              |
| ctharir                   | string | R phase CT side harmonic                    |
| ctharis                   | string | S phase CT side harmonic                    |
| ctharit                   | string | T phase CT side harmonic                    |
| compqr                    | string | R phase compensation reactive power         |
| compqs                    | string | S phase compensation reactive power         |
| compqt                    | string | T phase compensation reactive power         |
| compharir                 | string | R phase compensation harmonic               |
| compharis                 | string | S phase compensation harmonic               |
| compharit                 | string | T phase compensation harmonic               |
| pidStatus                 | string | PID status                                  |
| faultType                 | string | Fault code                                  |
| faultCode1                | string | Fault code                                  |
| faultCode2                | string | Fault code                                  |
| warnCode                  | string | Warning code                                |
| opFullwatt                | string | Output power limit                          |
| deratingMode              | string | Derating mode                               |
| pf                        | string | PF value                                    |
| pBusVoltage               | string | P Bus voltage                               |
| nBusVoltage               | string | N Bus voltage                               |
| temperature               | string | AMTemp1 (℃)                                 |
| temperature2              | string | INVTemp (℃)                                 |
| temperature3              | string | BTTemp (℃)                                  |
| temperature4              | string | OUTTemp (℃)                                 |
| temperature5              | string | AMTemp2 (℃)                                 |
| ipmTemperature            | string | IPM temperature                             |
| rac                       | string | Reactive power Var                          |
| eRacToday                 | string | Reactive power today kVarh                  |
| eRacTotal                 | string | Total reactive power kVarh                  |
| strFault                  | string | String error                                |
| dwStringWarningValue1     | string |                                              |
| wStringStatusValue        | string |                                              |
| wPIDFaultValue            | string |                                              |
| epv1Today                 | string | PV1 generation today                        |
| epv1Total                 | string | Total PV1 generation                        |
| epv2Today                 | string | PV2 generation today                        |
| epv2Total                 | string | Total PV2 generation                        |
| epv3Today                 | string | PV3 generation today                        |
| epv3Total                 | string | Total PV3 generation                        |
| epv4Today                 | string | PV4 generation today                        |
| epv4Total                 | string | Total PV4 generation                        |
| epv5Today                 | string | PV5 generation today                        |
| epv5Total                 | string | Total PV5 generation                        |
| epv6Today                 | string | PV6 generation today                        |
| epv6Total                 | string | Total PV6 generation                        |
| epv7Today                 | string | PV7 generation today                        |
| epv7Total                 | string | Total PV7 generation                        |
| epv8Today                 | string | PV8 generation today                        |
| epv8Total                 | string | Total PV8 generation                        |
| eacToday                  | string | Generation today                            |
| eacTotal                  | string | Total generation                            |
| epvTotal                  | string | Total PV generation                         |
| timeTotal                 | string | Total operating time                        |

**Remarks**

- The retrieval frequency is once every 5 minutes within the interval.


---

# 25. Basic information of the spa

*Page ID: `11292923430103270`*

**Brief Description:**

- Data return format for basic information of spa equipment and description of some basic information parameters.
- `Only applicable for: bulk retrieval of basic equipment information.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;spa&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;serialNum&quot;: &quot;MTN0H6800E&quot;,
                &quot;portName&quot;: &quot;ShinePano - XGD6CMM2VY&quot;,
                &quot;dataLogSn&quot;: &quot;XGD6CMM2VY&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;MTN0H6800E&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;RA1.0&quot;,
                &quot;model&quot;: 1710134400000,
                &quot;innerVersion&quot;: &quot;RBCA050306&quot;,
                &quot;lost&quot;: true,
                &quot;status&quot;: -1,
                &quot;tcpServerIp&quot;: &quot;127.0.0.1&quot;,
                &quot;lastUpdateTime&quot;: 1716435475000,
                &quot;sysTime&quot;: &quot;2024-05-23 11:34&quot;,
                &quot;communicationVersion&quot;: &quot;ZCBC-0006&quot;,
                &quot;deviceType&quot;: 2,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;energyMonth&quot;: 0.0,
                &quot;energyDayMap&quot;: {},
                &quot;onOff&quot;: 1,
                &quot;pmax&quot;: 3000,
                &quot;lcdLanguage&quot;: 1,
                &quot;countrySelected&quot;: 0,
                &quot;wselectBaudrate&quot;: 0,
                &quot;comAddress&quot;: 1,
                &quot;manufacturer&quot;: &quot;   New Energy   &quot;,
                &quot;dtc&quot;: 3735,
                &quot;modbusVersion&quot;: 307,
                &quot;floatChargeCurrentLimit&quot;: 600.0,
                &quot;vbatWarning&quot;: 480.0,
                &quot;vbatWarnClr&quot;: 5.0,
                &quot;vbatStopForDischarge&quot;: 4.7,
                &quot;vbatStopForCharge&quot;: 5.75,
                &quot;vbatStartForDischarge&quot;: 48.0,
                &quot;vbatStartforCharge&quot;: 58.0,
                &quot;batTempLowerLimitD&quot;: 110.0,
                &quot;batTempUpperLimitD&quot;: 70.0,
                &quot;batTempLowerLimitC&quot;: 110.0,
                &quot;batTempUpperLimitC&quot;: 60.0,
                &quot;forcedDischargeTimeStart1&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart2&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart3&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop1&quot;: &quot;23:0&quot;,
                &quot;forcedDischargeTimeStop2&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop3&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart1&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart2&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart3&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop1&quot;: &quot;23:0&quot;,
                &quot;forcedChargeTimeStop2&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop3&quot;: &quot;0:0&quot;,
                &quot;bctMode&quot;: 2,
                &quot;bctAdjust&quot;: 0,
                &quot;wdisChargeSOCLowLimit1&quot;: 10,
                &quot;wdisChargeSOCLowLimit2&quot;: 10,
                &quot;wchargeSOCLowLimit1&quot;: 100,
                &quot;wchargeSOCLowLimit2&quot;: 100,
                &quot;priorityChoose&quot;: 2,
                &quot;chargePowerCommand&quot;: 100,
                &quot;disChargePowerCommand&quot;: 100,
                &quot;bagingTestStep&quot;: 0,
                &quot;batteryType&quot;: 1,
                &quot;epsFunEn&quot;: 0,
                &quot;epsVoltSet&quot;: 0,
                &quot;epsFreqSet&quot;: 0,
                &quot;loadFirstStartTime1&quot;: &quot;null&quot;,
                &quot;loadFirstStopTime1&quot;: &quot;null&quot;,
                &quot;loadFirstStartTime2&quot;: &quot;null&quot;,
                &quot;loadFirstStopTime2&quot;: &quot;null&quot;,
                &quot;loadFirstStartTime3&quot;: &quot;null&quot;,
                &quot;loadFirstStopTime3&quot;: &quot;null&quot;,
                &quot;gridFirstSwitch1&quot;: 1,
                &quot;gridFirstSwitch2&quot;: 0,
                &quot;gridFirstSwitch3&quot;: 0,
                &quot;batFirstSwitch1&quot;: 0,
                &quot;batFirstSwitch2&quot;: 0,
                &quot;batFirstSwitch3&quot;: 0,
                &quot;loadFirstSwitch1&quot;: 0,
                &quot;loadFirstSwitch2&quot;: 0,
                &quot;loadFirstSwitch3&quot;: 0,
                &quot;vacHigh&quot;: 263.0,
                &quot;vacLow&quot;: 186.0,
                &quot;buckUpsFunEn&quot;: 1,
                &quot;buckUPSVoltSet&quot;: 0,
                &quot;upsFreqSet&quot;: 0,
                &quot;pfCMDmemoryState&quot;: 0,
                &quot;activePRate&quot;: 100,
                &quot;reactivePRate&quot;: 100,
                &quot;powerFactor&quot;: 10000,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;chargeTime1&quot;: null,
                &quot;chargeTime2&quot;: null,
                &quot;chargeTime3&quot;: null,
                &quot;dischargeTime1&quot;: null,
                &quot;dischargeTime2&quot;: null,
                &quot;dischargeTime3&quot;: null,
                &quot;pv_on_off&quot;: null,
                &quot;pf_sys_year&quot;: null,
                &quot;pv_grid_voltage_high&quot;: null,
                &quot;pv_grid_voltage_low&quot;: null,
                &quot;spa_off_grid_enable&quot;: null,
                &quot;spa_ac_discharge_frequency&quot;: null,
                &quot;spa_ac_discharge_voltage&quot;: null,
                &quot;pv_pf_cmd_memory_state&quot;: null,
                &quot;pv_active_p_rate&quot;: null,
                &quot;pv_reactive_p_rate&quot;: null,
                &quot;pv_reactive_p_rate_two&quot;: null,
                &quot;backflow_setting&quot;: null,
                &quot;pv_power_factor&quot;: null,
                &quot;userName&quot;: null,
                &quot;modelText&quot;: &quot;A0B1D0T4PFU2M2S0&quot;,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;equipmentType&quot;: null,
                &quot;sysTimeText&quot;: &quot;2024-05-23 11:34:33&quot;,
                &quot;wloadSOCLowLimit1&quot;: 0,
                &quot;wloadSOCLowLimit2&quot;: 10,
                &quot;invVersion&quot;: 1,
                &quot;batSerialNum&quot;: null,
                &quot;mcVersion&quot;: &quot;-0000&quot;,
                &quot;monitorVersion&quot;: &quot;FFFF-30840&quot;,
                &quot;forcedDischargeTimeStart4&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop4&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart5&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop5&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStart6&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeTimeStop6&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart4&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop4&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart5&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop5&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStart6&quot;: &quot;0:0&quot;,
                &quot;forcedChargeTimeStop6&quot;: &quot;0:0&quot;,
                &quot;forcedDischargeStopSwitch4&quot;: 0,
                &quot;forcedDischargeStopSwitch5&quot;: 0,
                &quot;forcedDischargeStopSwitch6&quot;: 0,
                &quot;forcedChargeStopSwitch4&quot;: 0,
                &quot;forcedChargeStopSwitch5&quot;: 0,
                &quot;forcedChargeStopSwitch6&quot;: 0,
                &quot;batSysRateEnergy&quot;: 0.0,
                &quot;oldErrorFlag&quot;: 0,
                &quot;region&quot;: 0,
                &quot;vppOpen&quot;: 0,
                &quot;underExcited&quot;: 0,
                &quot;exportLimit&quot;: 0,
                &quot;exportLimitPowerRate&quot;: 0.0,
                &quot;failsafe&quot;: 0,
                &quot;acChargeEnable&quot;: 0,
                &quot;newSwVersionFlag&quot;: 0,
                &quot;batPackNum&quot;: 0,
                &quot;offGridDischargeSOC&quot;: 20,
                &quot;level&quot;: 4,
                &quot;children&quot;: null,
                &quot;treeID&quot;: &quot;ST_MTN0H6800E&quot;,
                &quot;treeName&quot;: &quot;MTN0H6800E&quot;,
                &quot;parentID&quot;: &quot;LIST_XGD6CMM2VY_96&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-23 11:37:55&quot;,
                &quot;statusText&quot;: &quot;spa.status.lost&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-----|:-----|-----|
| serialNum | String | Serial Number |
| portName | String | Communication Port Information (Type and Address) |
| alias | String | Alias |
| location | String | Location |
| addr=0 | int | Inverter Address |
| fwVersion | String | Firmware Version |
| model | long | Model |
| innerVersion | String | Internal Version Number |
| lost=true | boolean | Communication Loss Indicator |
| status=-1 | int | Spa Status (0: Waiting Mode, 1: Self-check Mode, 3: Fault Mode, 4: Upgrading, 5-8: Normal Mode) |
| tcpServerIp | String | TCP Server IP Address |
| lastUpdateTime | Date | Last Update Time |
| sysTime | Calendar | System Time |
| communicationVersion | String | Communication Version Number |
| onOff | int | Power On/Off |
| pmax | String | Rated Power |
| lcdLanguage | int | LCD Language |
| countrySelected | int | Country Selection |
| wselectBaudrate | String | Baud Rate Selection |
| comAddress | int | Communication Address |
| manufacturer | String | Manufacturer Code |
| dtc | int | Device Code 43 |
| modbusVersion | int | MODBUS Version |
| floatChargeCurrentLimit | float | Float Charge Current Limit |
| vbatWarning | String | Battery Low Voltage Warning Point |
| vbatWarnClr | String | Battery Low Voltage Recovery Point |
| vbatStopForDischarge | String | Battery Discharge Stop Voltage |
| vbatStopForCharge | String | Battery Charge Stop Voltage |
| vbatStartForDischarge | String | Battery Discharge Lower Limit Voltage |
| vbatStartforCharge | String | Battery Charge Upper Limit Voltage |
| batTempLowerLimitD | String | Battery Discharge Temperature Lower Limit |
| batTempUpperLimitD | String | Battery Discharge Temperature Upper Limit |
| batTempLowerLimitC | String | Battery Charge Temperature Lower Limit |
| batTempUpperLimitC | String | Battery Charge Temperature Upper Limit |
| forcedDischargeTimeStart1 | String | Discharge 1 Start Time |
| forcedDischargeTimeStart2 | String | Discharge 2 Start Time |
| forcedDischargeTimeStart3 | String | Discharge 3 Start Time |
| forcedDischargeTimeStop1 | String | Discharge 1 Stop Time |
| forcedDischargeTimeStop2 | String | Discharge 2 Stop Time |
| forcedDischargeTimeStop3 | String | Discharge 3 Stop Time |
| forcedChargeTimeStart1 | String | Charge 1 Start Time |
| forcedChargeTimeStart2 | String | Charge 2 Start Time |
| forcedChargeTimeStart3 | String | Charge 3 Start Time |
| forcedChargeTimeStop1 | String | Charge 1 Stop Time |
| forcedChargeTimeStop2 | String | Charge 2 Stop Time |
| forcedChargeTimeStop3 | String | Charge 3 Stop Time |
| bctMode | int | Sensor Type (2: METER; 1: cWirelessCT; 0: cWiredCT) |
| bctAdjust | int | Sensor Adjustment Enable |
| wdisChargeSOCLowLimit1 | int | Load Priority Mode Discharge |
| wdisChargeSOCLowLimit2 | int | Grid Priority Mode Discharge |
| wchargeSOCLowLimit1 | int | Load Priority Mode Charge |
| wchargeSOCLowLimit2 | int | Battery Priority Mode Charge |
| priorityChoose | int | Energy Priority Selection |
| chargePowerCommand | String | Charge Power Setting |
| disChargePowerCommand | String | Discharge Power Setting |
| bagingTestStep | int | Battery Self-check |
| batteryType | int | Battery Type Selection |
| epsFunEn | int | Emergency Power Supply Enable |
| epsVoltSet | int | Emergency Power Supply Voltage |
| epsFreqSet | int | Emergency Power Supply Frequency |
| loadFirstStartTime1 | String | Load Priority Period 1 Start Time |
| loadFirstStopTime1 | String | Load Priority Period 1 End Time |
| loadFirstStartTime2 | String | Load Priority Period 2 Start Time |
| loadFirstStopTime2 | String | Load Priority Period 2 End Time |
| loadFirstStartTime3 | String | Load Priority Period 3 Start Time |
| loadFirstStopTime3 | String | Load Priority Period 3 End Time |
| gridFirstSwitch1 | int | Grid Priority Enable Bit 1082 |
| gridFirstSwitch2 | int | Grid Priority Enable Bit 1085 |
| gridFirstSwitch3 | int | Grid Priority Enable Bit 1088 |
| batFirstSwitch1 | int | Battery Priority Enable Bit 1 |
| batFirstSwitch2 | int | Battery Priority Enable Bit 2 |
| batFirstSwitch3 | int | Battery Priority Enable Bit 3 |
| loadFirstSwitch1 | int | Load Priority Enable Bit 1 |
| loadFirstSwitch2 | int | Load Priority Enable Bit 2 |
| loadFirstSwitch3 | int | Load Priority Enable Bit 3 |
| vacHigh | float | Grid Voltage Upper Limit |
| vacLow | float | Grid Voltage Lower Limit |
| buckUpsFunEn | int | Off-grid Enable |
| buckUPSVoltSet | int | Off-grid Voltage |
| upsFreqSet | int | Off-grid Frequency |
| pfCMDmemoryState | int | PF Command Storage Setting |
| activePRate | String | Active Power Setting |
| reactivePRate | String | Reactive Power Setting |
| powerFactor | int | PF Value Setting |
| chargeTime1 | String | Charge Time Period 1 |
| chargeTime2 | String | Charge Time Period 2 |
| chargeTime3 | String | Charge Time Period 3 |
| dischargeTime1 | String | Discharge Time Period 1 |
| dischargeTime2 | String | Discharge Time Period 2 |
| dischargeTime3 | String | Discharge Time Period 3 |
| pv_on_off | String | Power On/Off |
| pf_sys_year | String | Time Setting |
| pv_grid_voltage_high | String | Grid Voltage Upper Limit |
| pv_grid_voltage_low | String | Grid Voltage Lower Limit |
| spa_off_grid_enable | String | Off-grid Enable |
| spa_ac_discharge_frequency | String | Off-grid Frequency |
| spa_ac_discharge_voltage | String | Off-grid Voltage |
| pv_pf_cmd_memory_state | String | PF Command Storage Setting |
| pv_active_p_rate | String | Active Power Setting |
| pv_reactive_p_rate | String | Reactive Power Setting |
| pv_reactive_p_rate_two | String | Reactive Power Capacity |
| backflow_setting | String | Anti-backflow Setting |
| pv_power_factor | String | PF Value Setting |
| plantId | int | Plant ID |
| plantname | String | Plant Name |
| pCharge | String | Charge Power |
| pDischarge | String | Discharge Power |

**Remarks**
- The retrieval frequency is once every 5 minutes.

---

# 26. The last detailed data of the spa

*Page ID: `11292924339104189`*

**Brief Description:**

- The data format and parameter description of the last detailed data of spa equipment.
- `Only applicable for: Batch retrieval of the last data of equipment.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;spa&quot;: [
            {
                &quot;serialNum&quot;: &quot;MTN0H6800E&quot;,
                &quot;dataLogSn&quot;: &quot;XGD6CMM2VY&quot;,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716435473718,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 9,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;pac&quot;: 0.3,
                &quot;fac&quot;: 49.99,
                &quot;vac1&quot;: 227.3,
                &quot;pac1&quot;: 0.0,
                &quot;eacToday&quot;: 0.0,
                &quot;eacTotal&quot;: 6.5,
                &quot;timeTotal&quot;: 265549.0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 2,
                &quot;batteryType&quot;: 1,
                &quot;uwSysWorkMode&quot;: 9,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 33280,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 4,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 0.0,
                &quot;soc&quot;: 0,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 0.0,
                &quot;batteryTemperature&quot;: 0.0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etogridTotal&quot;: 1.0,
                &quot;edischarge1Today&quot;: 0.0,
                &quot;edischarge1Total&quot;: 6.8,
                &quot;echarge1Today&quot;: 0.0,
                &quot;echarge1Total&quot;: 7.6,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;upsFac&quot;: 0.0,
                &quot;upsVac1&quot;: 225.4,
                &quot;upsPac1&quot;: 0.0,
                &quot;upsLoadpercent&quot;: 0,
                &quot;upsPF&quot;: 1000.0,
                &quot;bmsStatusOld&quot;: 0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsErrorOld&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;bmsSOC&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsMaxDischgCurr&quot;: 0.0,
                &quot;bmsGaugeRM&quot;: 0.0,
                &quot;bmsGaugeFCC&quot;: 0,
                &quot;bmsFW&quot;: 0,
                &quot;bmsDeltaVolt&quot;: 0.0,
                &quot;bmsCycleCnt&quot;: 0,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0.0,
                &quot;bmsWarnInfoOld&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsMCUVersion&quot;: 0,
                &quot;bmsInfo&quot;: 0,
                &quot;bmsPackInfo&quot;: 0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCell1Volt&quot;: 0.0,
                &quot;bmsCell2Volt&quot;: 0.0,
                &quot;bmsCell3Volt&quot;: 0.0,
                &quot;bmsCell4Volt&quot;: 0.0,
                &quot;bmsCell5Volt&quot;: 0.0,
                &quot;bmsCell6Volt&quot;: 0.0,
                &quot;bmsCell7Volt&quot;: 0.0,
                &quot;bmsCell8Volt&quot;: 0.0,
                &quot;bmsCell9Volt&quot;: 0.0,
                &quot;bmsCell10Volt&quot;: 0.0,
                &quot;bmsCell11Volt&quot;: 0.0,
                &quot;bmsCell12Volt&quot;: 0.0,
                &quot;bmsCell13Volt&quot;: 0.0,
                &quot;bmsCell14Volt&quot;: 0.0,
                &quot;bmsCell15Volt&quot;: 0.0,
                &quot;bmsCell16Volt&quot;: 0.0,
                &quot;acChargeEnergyToday&quot;: 0.0,
                &quot;acChargeEnergyTotal&quot;: 8.3,
                &quot;acChargePower&quot;: 0.0,
                &quot;vBus1&quot;: 4.3,
                &quot;vBus2&quot;: 4.8,
                &quot;temp1&quot;: 28.300001,
                &quot;temp2&quot;: 26.7,
                &quot;temp3&quot;: 27.7,
                &quot;vBatDsp&quot;: 2.2,
                &quot;sysEn&quot;: 20992,
                &quot;epvInverterToday&quot;: 0.0,
                &quot;epvInverterTotal&quot;: 0.0,
                &quot;ppvInverter&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;upsIac1&quot;: 0.0,
                &quot;upsIac2&quot;: 0.0,
                &quot;upsIac3&quot;: 0.0,
                &quot;upsVac2&quot;: 0.0,
                &quot;upsVac3&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;upsPac3&quot;: 0.0,
                &quot;esystemTotal&quot;: 5.9,
                &quot;esystemToday&quot;: 0.0,
                &quot;eselftoday&quot;: 0.0,
                &quot;eselftotal&quot;: 5.9,
                &quot;psystem&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;monitor&quot;: 1,
                &quot;uwMaxCellVol&quot;: 0.0,
                &quot;uwMinCellVol&quot;: 0.0,
                &quot;bModuleNum&quot;: 0,
                &quot;bTotalCellNum&quot;: 0,
                &quot;uwMaxVoltCellNo&quot;: 0,
                &quot;uwMinVoltCellNo&quot;: 0,
                &quot;uwMaxTemprCell&quot;: 0.0,
                &quot;uwMinTemprCell&quot;: 0.0,
                &quot;uwMaxTemprCellNo&quot;: 0,
                &quot;uwMinTemprCellNo&quot;: 0,
                &quot;protectPackId&quot;: 0,
                &quot;maxSOC&quot;: 0,
                &quot;minSOC&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;bmsError3&quot;: 0,
                &quot;bmsWarnInfo2&quot;: 0,
                &quot;bmsHighestSoftVersion&quot;: 0,
                &quot;bmsHardwareVersion&quot;: 0,
                &quot;bmsRequestType&quot;: 0,
                &quot;accDischargePackSn&quot;: 0,
                &quot;accdischargePower&quot;: 0.0,
                &quot;accChargePackSn&quot;: 0,
                &quot;accChargePower&quot;: 0.0,
                &quot;firstBattFaultSn&quot;: 0,
                &quot;secondBattFaultSn&quot;: 0,
                &quot;thirdBattFaultSn&quot;: 0,
                &quot;fourthBattFaultSn&quot;: 0,
                &quot;battHistoryFaultCode1&quot;: 0,
                &quot;battHistoryFaultCode2&quot;: 0,
                &quot;battHistoryFaultCode3&quot;: 0,
                &quot;battHistoryFaultCode4&quot;: 0,
                &quot;battHistoryFaultCode5&quot;: 0,
                &quot;battHistoryFaultCode6&quot;: 0,
                &quot;battHistoryFaultCode7&quot;: 0,
                &quot;battHistoryFaultCode8&quot;: 0,
                &quot;numberOfBattCodes&quot;: 0,
                &quot;pmR&quot;: 0,
                &quot;pmS&quot;: 0,
                &quot;pmT&quot;: 0,
                &quot;pacR&quot;: 0,
                &quot;pacS&quot;: 0,
                &quot;pacT&quot;: 0,
                &quot;plocalLoadR2&quot;: 0,
                &quot;plocalLoadS&quot;: 0,
                &quot;plocalLoadT&quot;: 0,
                &quot;uwDspInvDebugData&quot;: 0,
                &quot;uwDspInvDebugData1&quot;: 0,
                &quot;uwDspInvDebugData2&quot;: 0,
                &quot;uwDspInvDebugData3&quot;: 0,
                &quot;uwDspInvDebugData4&quot;: 0,
                &quot;uwDspDcDcDebugData&quot;: 0,
                &quot;uwDspDcDcDebugData1&quot;: 0,
                &quot;uwDspDcDcDebugData2&quot;: 0,
                &quot;uwDspDcDcDebugData3&quot;: 0,
                &quot;uwDspDcDcDebugData4&quot;: 0,
                &quot;bmsHardwareVersion2&quot;: 0,
                &quot;moduleSeriesQty&quot;: 0,
                &quot;spaBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-05-23 11:37:53&quot;,
                &quot;socText&quot;: &quot;0%&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Bypass&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description**

| Type | Parameter Name | Description |
|:-----  |:-----|----- |
| String | serialNum | Serial Number |
| Calendar | calendar | Time |
| boolean | withTime | Whether the received data includes time |
| boolean | isAgain | Whether it is a retransmission |
| boolean | lost = true | Whether communication is lost |
| double | pac | Inverter output power |
| float | fac | Grid frequency |
| float | vac1 | Grid voltage |
| double | pac1 | Inverter apparent output power |
| float | eacToday | Inverter daily output energy |
| double | eacTotal | Inverter total output energy |
| double | timeTotal | Total operating time |
| int | faultCode | Inverter fault code |
| int | faultBitCode | Inverter fault bit code |
| int | warnCode | Warning code |
| int | errorCode | Error code |
| int | uwSysWorkMode | System working mode |
| double | pdischarge1 | Battery discharge power |
| double | pcharge1 | Battery charge power |
| float | vbat | Battery voltage |
| int | soc | Battery state of charge |
| double | pacToUserR | Grid forward power |
| double | pacToUserTotal | Grid total forward power |
| double | pacToGridR | Grid reverse power |
| double | pacToGridTotal | Grid total reverse power |
| double | plocalLoadR | Local load power consumption |
| double | plocalLoadTotal | Local total load power consumption |
| float | batteryTemperature | Battery temperature |
| double | etoUserToday | Grid daily energy output |
| double | etoUserTotal | Grid total energy output |
| double | etoGridToday | Grid daily energy intake |
| double | etogridTotal | Grid total energy intake |
| double | edischarge1Today | Battery daily discharge energy |
| double | edischarge1Total | Battery total discharge energy |
| double | echarge1Today | Battery daily charge energy |
| double | echarge1Total | Battery total charge energy |
| double | elocalLoadToday | Local load daily energy consumption |
| double | elocalLoadTotal | Local total load energy consumption |
| float | upsFac | UPS frequency |
| float | upsVac1 | UPS voltage |
| double | upsPac1 | UPS apparent output power |
| int | upsLoadpercent | UPS load percentage |
| float | upsPF | UPS power factor |
| int | bmsStatusOld | Battery historical status |
| int | bmsStatus | Battery status |
| int | bmsErrorOld | Battery historical fault |
| int | bmsError | Battery fault |
| int | bmsSOC | Battery state of charge |
| float | bmsBatteryVolt | Battery voltage |
| float | bmsBatteryCurr | Battery current |
| float | bmsBatteryTemp | Battery temperature |
| float | bmsMaxCurr | Maximum charge-discharge current |
| float | bmsMaxDischgCurr | Maximum discharge current |
| float | bmsGaugeRM | System capacity |
| int | bmsGaugeFCC | Rated capacity |
| int | bmsFW | BMS firmware version |
| float | bmsDeltaVolt | Battery cell voltage difference |
| int | bmsCycleCnt | Battery cycle count |
| int | bmsSOH | Battery state of health |
| float | bmsConstantVolt | Battery constant voltage charging point |
| int | bmsWarnInfoOld | Battery historical warning information |
| int | bmsWarnInfo | Battery warning information |
| int | bmsMCUVersion | BMS firmware version |
| int | bmsInfo | BMS information |
| int | bmsPackInfo | Battery pack information |
| int | bmsUsingCap | Battery pack power type |
| float | bmsCell1Volt | Battery cell 1 voltage |
| float | bmsCell2Volt | Battery cell 2 voltage |
| float | bmsCell3Volt | Battery cell 3 voltage |
| float | bmsCell4Volt | Battery cell 4 voltage |
| float | bmsCell5Volt | Battery cell 5 voltage |
| float | bmsCell6Volt | Battery cell 6 voltage |
| float | bmsCell7Volt | Battery cell 7 voltage |
| float | bmsCell8Volt | Battery cell 8 voltage |
| float | bmsCell9Volt | Battery cell 9 voltage |
| float | bmsCell10Volt | Battery cell 10 voltage |
| float | bmsCell11Volt | Battery cell 11 voltage |
| float | bmsCell12Volt | Battery cell 12 voltage |
| float | bmsCell13Volt | Battery cell 13 voltage |
| float | bmsCell14Volt | Battery cell 14 voltage |
| float | bmsCell15Volt | Battery cell 15 voltage |
| float | bmsCell16Volt | Battery cell 16 voltage |
| double | acChargeEnergyToday | AC daily charge energy |
| double | acChargeEnergyTotal | AC total charge energy |
| double | acChargePower | AC charge power |
| float | vBus1 | Bus1 voltage |
| float | vBus2 | Bus2 voltage |
| float | temp1 | Temperature 1 |
| float | temp2 | Temperature 2 |
| float | vBatDsp | DSP collected battery voltage |
| int | sysEn | System enable bit |
| double | epvInverterToday | PV inverter daily energy generation |
| double | epvInverterTotal | PV inverter total energy generation |
| double | ppvInverter | PV inverter power generation |

 **Notes** 
- Retrieval frequency is once per 5 minutes.

---

# 27. Historical Data of Spa Equipment

*Page ID: `11292925068299407`*

  
**Brief Description:**

- The data format and parameter description of historical data for spa equipment.
- `Only applicable for: Retrieving all detailed data of a specific device for a particular day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;MTN0H6800E&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1713952554000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;pac&quot;: 0.0,
                &quot;fac&quot;: 49.97,
                &quot;vac1&quot;: 226.9,
                &quot;pac1&quot;: 3016.8,
                &quot;eacToday&quot;: 0.2,
                &quot;eacTotal&quot;: 3.3,
                &quot;timeTotal&quot;: 140162.5,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 1,
                &quot;batteryType&quot;: 1,
                &quot;uwSysWorkMode&quot;: 6,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 2708.0,
                &quot;vbat&quot;: 54.4,
                &quot;soc&quot;: 88,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 0.0,
                &quot;batteryTemperature&quot;: 32.0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etogridTotal&quot;: 0.4,
                &quot;edischarge1Today&quot;: 0.2,
                &quot;edischarge1Total&quot;: 3.4,
                &quot;echarge1Today&quot;: 2.8,
                &quot;echarge1Total&quot;: 2.8,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.2,
                &quot;upsFac&quot;: 0.0,
                &quot;upsVac1&quot;: 225.1,
                &quot;upsPac1&quot;: 0.0,
                &quot;upsLoadpercent&quot;: 0,
                &quot;upsPF&quot;: 1000.0,
                &quot;bmsStatusOld&quot;: 0,
                &quot;bmsStatus&quot;: 98,
                &quot;bmsErrorOld&quot;: 0,
                &quot;bmsError&quot;: 0,
                &quot;bmsSOC&quot;: 88,
                &quot;bmsBatteryVolt&quot;: 54.4,
                &quot;bmsBatteryCurr&quot;: 50.2,
                &quot;bmsBatteryTemp&quot;: 32.0,
                &quot;bmsMaxCurr&quot;: 104.2,
                &quot;bmsMaxDischgCurr&quot;: 104.2,
                &quot;bmsGaugeRM&quot;: 115.5,
                &quot;bmsGaugeFCC&quot;: 128,
                &quot;bmsFW&quot;: 34438,
                &quot;bmsDeltaVolt&quot;: 7.0,
                &quot;bmsCycleCnt&quot;: 24,
                &quot;bmsSOH&quot;: 100,
                &quot;bmsConstantVolt&quot;: 56.8,
                &quot;bmsWarnInfoOld&quot;: 0,
                &quot;bmsWarnInfo&quot;: 0,
                &quot;bmsMCUVersion&quot;: 34438,
                &quot;bmsInfo&quot;: 16720,
                &quot;bmsPackInfo&quot;: 16720,
                &quot;bmsUsingCap&quot;: 0,
                &quot;bmsCell1Volt&quot;: 3.405,
                &quot;bmsCell2Volt&quot;: 3.399,
                &quot;bmsCell3Volt&quot;: 0.001,
                &quot;bmsCell4Volt&quot;: 3.6,
                &quot;bmsCell5Volt&quot;: 3.402,
                &quot;bmsCell6Volt&quot;: 3.401,
                &quot;bmsCell7Volt&quot;: 3.399,
                &quot;bmsCell8Volt&quot;: 3.403,
                &quot;bmsCell9Volt&quot;: 3.401,
                &quot;bmsCell10Volt&quot;: 3.4,
                &quot;bmsCell11Volt&quot;: 3.399,
                &quot;bmsCell12Volt&quot;: 3.4,
                &quot;bmsCell13Volt&quot;: 3.401,
                &quot;bmsCell14Volt&quot;: 3.4,
                &quot;bmsCell15Volt&quot;: 3.399,
                &quot;bmsCell16Volt&quot;: 3.4,
                &quot;acChargeEnergyToday&quot;: 3.0,
                &quot;acChargeEnergyTotal&quot;: 3.1,
                &quot;acChargePower&quot;: 3009.7,
                &quot;vBus1&quot;: 419.0,
                &quot;vBus2&quot;: 335.0,
                &quot;temp1&quot;: 52.0,
                &quot;temp2&quot;: 46.0,
                &quot;temp3&quot;: 45.0,
                &quot;vBatDsp&quot;: 55.3,
                &quot;sysEn&quot;: 20994,
                &quot;epvInverterToday&quot;: 0.0,
                &quot;epvInverterTotal&quot;: 0.0,
                &quot;ppvInverter&quot;: 0.0,
                &quot;iac1&quot;: 12.8,
                &quot;iac2&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;upsIac1&quot;: 0.0,
                &quot;upsIac2&quot;: 0.0,
                &quot;upsIac3&quot;: 0.0,
                &quot;upsVac2&quot;: 0.0,
                &quot;upsVac3&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;upsPac3&quot;: 0.0,
                &quot;esystemTotal&quot;: 2.5,
                &quot;esystemToday&quot;: 0.3,
                &quot;eselftoday&quot;: 0.3,
                &quot;eselftotal&quot;: 2.5,
                &quot;psystem&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;monitor&quot;: 0,
                &quot;uwMaxCellVol&quot;: 3.405,
                &quot;uwMinCellVol&quot;: 3.399,
                &quot;bModuleNum&quot;: 1,
                &quot;bTotalCellNum&quot;: 16,
                &quot;uwMaxVoltCellNo&quot;: 4,
                &quot;uwMinVoltCellNo&quot;: 7,
                &quot;uwMaxTemprCell&quot;: 35.3,
                &quot;uwMinTemprCell&quot;: 31.5,
                &quot;uwMaxTemprCellNo&quot;: 3,
                &quot;uwMinTemprCellNo&quot;: 1,
                &quot;protectPackId&quot;: 0,
                &quot;maxSOC&quot;: 88,
                &quot;minSOC&quot;: 88,
                &quot;bmsError2&quot;: 0,
                &quot;bmsError3&quot;: 0,
                &quot;bmsWarnInfo2&quot;: 0,
                &quot;bmsHighestSoftVersion&quot;: 0,
                &quot;bmsHardwareVersion&quot;: 35,
                &quot;bmsRequestType&quot;: 192,
                &quot;accDischargePackSn&quot;: 1,
                &quot;accdischargePower&quot;: 139.1,
                &quot;accChargePackSn&quot;: 1,
                &quot;accChargePower&quot;: 158.2,
                &quot;firstBattFaultSn&quot;: 0,
                &quot;secondBattFaultSn&quot;: 0,
                &quot;thirdBattFaultSn&quot;: 0,
                &quot;fourthBattFaultSn&quot;: 0,
                &quot;battHistoryFaultCode1&quot;: 0,
                &quot;battHistoryFaultCode2&quot;: 0,
                &quot;battHistoryFaultCode3&quot;: 0,
                &quot;battHistoryFaultCode4&quot;: 0,
                &quot;battHistoryFaultCode5&quot;: 0,
                &quot;battHistoryFaultCode6&quot;: 0,
                &quot;battHistoryFaultCode7&quot;: 0,
                &quot;battHistoryFaultCode8&quot;: 0,
                &quot;numberOfBattCodes&quot;: 0,
                &quot;pmR&quot;: 0,
                &quot;pmS&quot;: 0,
                &quot;pmT&quot;: 0,
                &quot;pacR&quot;: 0,
                &quot;pacS&quot;: 0,
                &quot;pacT&quot;: 0,
                &quot;plocalLoadR2&quot;: 0,
                &quot;plocalLoadS&quot;: 0,
                &quot;plocalLoadT&quot;: 0,
                &quot;uwDspInvDebugData&quot;: 0,
                &quot;uwDspInvDebugData1&quot;: 0,
                &quot;uwDspInvDebugData2&quot;: 0,
                &quot;uwDspInvDebugData3&quot;: 0,
                &quot;uwDspInvDebugData4&quot;: 0,
                &quot;uwDspDcDcDebugData&quot;: 0,
                &quot;uwDspDcDcDebugData1&quot;: 0,
                &quot;uwDspDcDcDebugData2&quot;: 0,
                &quot;uwDspDcDcDebugData3&quot;: 0,
                &quot;uwDspDcDcDebugData4&quot;: 0,
                &quot;bmsHardwareVersion2&quot;: 0,
                &quot;moduleSeriesQty&quot;: 3400,
                &quot;spaBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-04-24 17:55:54&quot;,
                &quot;socText&quot;: &quot;88%&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Bat Online&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;
            },
		     &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Descriptions**

| Type | Parameter Name | Description |
|:-----|:---------------|:------------|
| String | serialNum | Serial Number |
| Calendar | calendar | Time |
| boolean | withTime | Whether the received data includes the time |
| boolean | isAgain | Whether it is a retransmission |
| boolean | lost = true | Whether communication is lost |
| double | pac | Inverter output power |
| float | fac | Grid frequency |
| float | vac1 | Grid voltage |
| double | pac1 | Inverter output apparent power |
| float | eacToday | Inverter daily output energy |
| double | eacTotal | Inverter total output energy |
| double | timeTotal | Total running time |
| int | faultCode | Inverter fault code |
| int | faultBitCode | Inverter fault bit code |
| int | warnCode | Warning code |
| int | errorCode | Error code |
| int | uwSysWorkMode | System working mode |
| double | pdischarge1 | Battery discharge power |
| double | pcharge1 | Battery charge power |
| float | vbat | Battery voltage |
| int | soc | Battery state of charge |
| double | pacToUserR | Grid forward power |
| double | pacToUserTotal | Total grid forward power |
| double | pacToGridR | Grid reverse power |
| double | pacToGridTotal | Total grid reverse power |
| double | plocalLoadR | Local load power consumption |
| double | plocalLoadTotal | Total local load power consumption |
| float | batteryTemperature | Battery temperature |
| double | etoUserToday | Grid daily output energy |
| double | etoUserTotal | Total grid output energy |
| double | etoGridToday | Grid daily input energy |
| double | etoGridTotal | Total grid input energy |
| double | edischarge1Today | Battery daily discharge energy |
| double | edischarge1Total | Total battery discharge energy |
| double | echarge1Today | Battery daily charge energy |
| double | echarge1Total | Total battery charge energy |
| double | elocalLoadToday | Local load daily energy consumption |
| double | elocalLoadTotal | Total local load energy consumption |
| float | upsFac | UPS frequency |
| float | upsVac1 | UPS voltage |
| double | upsPac1 | UPS apparent power output |
| int | upsLoadpercent | UPS load percentage |
| float | upsPF | UPS power factor |
| int | bmsStatusOld | Historical battery status |
| int | bmsStatus | Battery status |
| int | bmsErrorOld | Historical battery fault |
| int | bmsError | Battery fault |
| int | bmsSOC | Battery state of charge |
| float | bmsBatteryVolt | Battery voltage |
| float | bmsBatteryCurr | Battery current |
| float | bmsBatteryTemp | Battery temperature |
| float | bmsMaxCurr | Maximum charge/discharge current |
| float | bmsMaxDischgCurr | Maximum discharge current |
| float | bmsGaugeRM | System capacity |
| int | bmsGaugeFCC | Rated capacity |
| int | bmsFW | BMS firmware version |
| float | bmsDeltaVolt | Voltage difference between battery cells |
| int | bmsCycleCnt | Battery cycle count |
| int | bmsSOH | Battery state of health |
| float | bmsConstantVolt | Battery constant voltage point |
| int | bmsWarnInfoOld | Historical battery warning information |
| int | bmsWarnInfo | Battery warning information |
| int | bmsMCUVersion | BMS firmware version |
| int | bmsInfo | BMS information |
| int | bmsPackInfo | Battery pack information |
| int | bmsUsingCap | Battery pack power type |
| float | bmsCell1Volt | Battery cell 1 voltage |
| float | bmsCell2Volt | Battery cell 2 voltage |
| float | bmsCell3Volt | Battery cell 3 voltage |
| float | bmsCell4Volt | Battery cell 4 voltage |
| float | bmsCell5Volt | Battery cell 5 voltage |
| float | bmsCell6Volt | Battery cell 6 voltage |
| float | bmsCell7Volt | Battery cell 7 voltage |
| float | bmsCell8Volt | Battery cell 8 voltage |
| float | bmsCell9Volt | Battery cell 9 voltage |
| float | bmsCell10Volt | Battery cell 10 voltage |
| float | bmsCell11Volt | Battery cell 11 voltage |
| float | bmsCell12Volt | Battery cell 12 voltage |
| float | bmsCell13Volt | Battery cell 13 voltage |
| float | bmsCell14Volt | Battery cell 14 voltage |
| float | bmsCell15Volt | Battery cell 15 voltage |
| float | bmsCell16Volt | Battery cell 16 voltage |
| double | acChargeEnergyToday | AC daily charge energy |
| double | acChargeEnergyTotal | Total AC charge energy |
| double | acChargePower | AC charge power |
| float | vBus1 | Bus1 voltage |
| float | vBus2 | Bus2 voltage |
| float | temp1 | Temperature 1 |
| float | temp2 | Temperature 2 |
| float | vBatDsp | DSP collected battery voltage |
| int | sysEn | System enable bit |
| double | epvInverterToday | PV inverter daily generated energy |
| double | epvInverterTotal | Total PV inverter generated energy |
| double | ppvInverter | PV inverter power |

**Notes**
- The frequency of data retrieval is once every 5 minutes.

---

# 28. Minimum basic information

*Page ID: `11292925501705236`*

  
**Brief Description:**

- Data return format for basic information of min devices and description of some basic information parameters
- `Only applicable for: batch retrieval of basic device information.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;min&quot;: [
            {
                &quot;id&quot;: 1627,
                &quot;serialNum&quot;: &quot;AFE494403F&quot;,
                &quot;portName&quot;: &quot;ShinePano - BLE094404C&quot;,
                &quot;dataLogSn&quot;: &quot;BLE094404C&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;AFE494403F&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;AK1.0&quot;,
                &quot;model&quot;: 720575940630937650,
                &quot;innerVersion&quot;: &quot;AKAA0501&quot;,
                &quot;lost&quot;: false,
                &quot;status&quot;: 1,
                &quot;tcpServerIp&quot;: &quot;47.119.160.91&quot;,
                &quot;lastUpdateTime&quot;: 1716535759000,
                &quot;sysTime&quot;: &quot;&quot;,
                &quot;deviceType&quot;: 0,
                &quot;communicationVersion&quot;: &quot;ZAAA-0004&quot;,
                &quot;pmax&quot;: 5000,
                &quot;comAddress&quot;: 1,
                &quot;dtc&quot;: 5200,
                &quot;countrySelected&quot;: 0,
                &quot;startTime&quot;: 30,
                &quot;restartTime&quot;: 60,
                &quot;wselectBaudrate&quot;: 0,
                &quot;trakerModel&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;batteryType&quot;: 0,
                &quot;batSeriesNum&quot;: 0,
                &quot;batParallelNum&quot;: 0,
                &quot;bctMode&quot;: 0,
                &quot;bctAdjust&quot;: 0,
                &quot;bagingTestStep&quot;: 0,
                &quot;vnormal&quot;: 1000.0,
                &quot;mppt&quot;: 513.0,
                &quot;batTempLowerLimitD&quot;: 0.0,
                &quot;batTempUpperLimitD&quot;: 0.0,
                &quot;batTempLowerLimitC&quot;: 0.0,
                &quot;batTempUpperLimitC&quot;: 0.0,
                &quot;vbatWarning&quot;: 0.0,
                &quot;vbatWarnClr&quot;: 0.0,
                &quot;modbusVersion&quot;: 305,
                &quot;manufacturer&quot;: &quot;   PV Inverter  &quot;,
                &quot;bdc1Sn&quot;:&quot;����������������&quot;,
                &quot;bdc1Model&quot;: &quot;0&quot;,
                &quot;bdc1Version&quot;:&quot;����-0&quot;,
                &quot;vbatStopForDischarge&quot;: 0.0,
                &quot;vbatStopForCharge&quot;: 0.0,
                &quot;vbatStartForDischarge&quot;: 0.0,
                &quot;userName&quot;: null,
                &quot;modelText&quot;: &quot;S0AB00D00T00P0FU00M0032&quot;,
                &quot;plantId&quot;: 0,
                &quot;plantname&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;power&quot;: 0.0,
                &quot;eToday&quot;: 0.0,
                &quot;eTotal&quot;: 0.0,
                &quot;tlxSetbean&quot;: null,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDayMap&quot;: {},
                &quot;energyMonth&quot;: 0.0,
                &quot;optimezerList&quot;: null,
                &quot;strNum&quot;: -1,
                &quot;liBatteryManufacturers&quot;: &quot;&quot;,
                &quot;liBatteryFwVersion&quot;: &quot;&quot;,
                &quot;bmsSoftwareVersion&quot;: &quot;&quot;,
                &quot;bmsCommunicationType&quot;: 0,
                &quot;monitorVersion&quot;: &quot;null&quot;,
                &quot;bdcMode&quot;: 0,
                &quot;bdcAuthversion&quot;: 0,
                &quot;hwVersion&quot;: &quot;null&quot;,
                &quot;vppOpen&quot;: 0,
                &quot;level&quot;: 4,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-24 15:29:19&quot;,
                &quot;children&quot;: null,
                &quot;treeName&quot;: &quot;AFE494403F&quot;,
                &quot;treeID&quot;: &quot;ST_AFE494403F&quot;,
                &quot;parentID&quot;: &quot;LIST_BLE094404C_22&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;statusText&quot;: &quot;tlx.status.checking&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

|Parameter Name|Type|Description|
|:-----  |:-----|----- |
|serialNum |string  |Device SN|
|lost |string  |Device online status (0: Online, 1: Offline)|
|status |int  |Device status (0: Waiting mode, 1: Self-check mode, 3: Fault mode, 4: Upgrading, 5,6,7,8: Normal mode)|
|alias |int  |Alias|
|location |string  |Address|
|dataLogSn |string  |Data logger serial number|
|pmax |string  |Rated power|
|power |string  |Current power|
|~~eToday~~ |string  |~~Today's generated power~~ (Deprecated)|
|~~eTotal~~ |string  |~~Total generated power~~ (Deprecated)|
|lastUpdateTime |string  |Last update time|
|tcpServerIp |string  |Server address|
|fwVersion |string  |Inverter version|
| addr = 0 |string  | Inverter address |
| model |string  | Model |
| innerVersion |string  | Internal version number |
| sysTime |string  | System time |
| deviceType |string  | 1:Mix, 0: Inverter |
| communicationVersion |string  | Communication version number |
| pmax |string  | Rated power; 0.1VA |
| comAddress |string  | Communication address 30 |
| dtc |string  | Device code |
| countrySelected |string  | Country selection |
| startTime |string  | Startup countdown |
| restartTime |string  | Reconnection countdown |
| wselectBaudrate |string  | Baud rate selection |
| trakerModel |string  | Task model |
| priorityChoose |string  | Energy priority selection; 0: Load, 1: Battery, 2: Grid |
| batteryType |string  | Battery type selection; 0: Lithium, 1: Lead-acid, 2: Other |
| batSeriesNum |string  | Number of battery series |
| batParallelNum |string  | Number of battery parallels |
| bctMode |string  | Sensor type; 2: METER, 1: Wireless CT, 0: Wired CT |
| bctAdjust |string  | Sensor adjustment enable; 0: Disable, 1: Enable |
| bagingTestStep |string  | Battery self-test; 0: Default, 1: Charge, 2: Discharge |
| vnormal |string  | Rated PV voltage; 0.1V |
| mppt |string  | MPPT voltage |
| batTempLowerLimitD |string  | Battery discharge lower temperature limit; 0.1℃ |
| batTempUpperLimitD |string  | Battery discharge upper temperature limit; 0.1℃ |
| batTempLowerLimitC |string  | Battery charge lower temperature limit; 0.1℃ |
| batTempUpperLimitC |string  | Battery charge upper temperature limit; 0.1℃ |
| vbatWarning |string  | Battery low voltage warning point; 0.1V |
| vbatWarnClr |string  | Battery low voltage recovery point; 0.1V |
| modbusVersion |string  | Modbus version |
| manufacturer |string  | Manufacturer code 34-41 |
| bdc1Sn |string  | BDC1 serial number |
| bdc1Model |string  | BDC1 model |
| bdc1Version |string  | BDC1 version |
| vbatStopForDischarge |string  | Battery discharge stop voltage; 0.01V |
| vbatStopForCharge |string  | Battery charge stop voltage; 0.01V |
| vbatStartForDischarge |string  | Battery discharge lower limit voltage; 0.01V |
| modelText |string  | Model |

**Notes**
- Retrieval frequency is once every 5 minutes or less


---

# 29. min the last detailed data

*Page ID: `11292926445680439`*

  
**Brief Description:**

- Data format and parameter description of the last detailed data of the min device.
- `Only applicable to: Batch retrieval of the last data of devices.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;min&quot;: [
            {
                &quot;serialNum&quot;: &quot;AFE494403F&quot;,
                &quot;dataLogSn&quot;: &quot;BLE094404C&quot;,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716619122927,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;isAgain&quot;: false,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 112.9,
                &quot;ppv1&quot;: 59.4,
                &quot;ppv2&quot;: 53.5,
                &quot;ppv3&quot;: 0.0,
                &quot;pac&quot;: 110.9,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;pacToLocalLoad&quot;: 110.9,
                &quot;timeTotal&quot;: 1.27984299E7,
                &quot;epsPac&quot;: 0.0,
                &quot;vpv1&quot;: 253.9,
                &quot;ipv1&quot;: 0.1,
                &quot;vpv2&quot;: 253.3,
                &quot;ipv2&quot;: 0.1,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;fac&quot;: 49.99,
                &quot;vac1&quot;: 226.8,
                &quot;iac1&quot;: 0.6,
                &quot;pac1&quot;: 112.2,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;vacRs&quot;: 226.8,
                &quot;vacSt&quot;: 0.0,
                &quot;vacTr&quot;: 0.0,
                &quot;eacToday&quot;: 2.0,
                &quot;eacTotal&quot;: 25799.8,
                &quot;epv1Today&quot;: 1.0,
                &quot;epv2Today&quot;: 1.0,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;temp1&quot;: 18.8,
                &quot;temp2&quot;: 0.0,
                &quot;temp3&quot;: 0.0,
                &quot;temp4&quot;: 0.0,
                &quot;temp5&quot;: 28.4,
                &quot;pBusVoltage&quot;: 358.4,
                &quot;nBusVoltage&quot;: 0.0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;invDelayTime&quot;: 0.0,
                &quot;pf&quot;: 1.0,
                &quot;epsPf&quot;: -1.0,
                &quot;dcVoltage&quot;: 0.0,
                &quot;epsFac&quot;: 0.0,
                &quot;epsVac1&quot;: 0.0,
                &quot;epsIac1&quot;: 0.0,
                &quot;epsPac1&quot;: 0.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;epsPac2&quot;: 0.0,
                &quot;epsVac3&quot;: 0.0,
                &quot;epsIac3&quot;: 0.0,
                &quot;epsPac3&quot;: 0.0,
                &quot;dciR&quot;: 5.0,
                &quot;dciS&quot;: 0.0,
                &quot;dciT&quot;: 0.0,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;faultType&quot;: 0,
                &quot;faultType1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;realOPPercent&quot;: 2,
                &quot;deratingMode&quot;: 0,
                &quot;bdcStatus&quot;: 0,
                &quot;dryContactStatus&quot;: 0,
                &quot;loadPercent&quot;: 0.0,
                &quot;uwSysWorkMode&quot;: 0,
                &quot;gfci&quot;: 5194,
                &quot;iso&quot;: 4508,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 0.0,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;epv1Total&quot;: 13630.1,
                &quot;epv2Total&quot;: 12371.8,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epvTotal&quot;: 26001.9,
                &quot;echargeToday&quot;: 0.0,
                &quot;echargeTotal&quot;: 0.0,
                &quot;edischargeToday&quot;: 0.0,
                &quot;edischargeTotal&quot;: 0.0,
                &quot;eacChargeToday&quot;: 0.0,
                &quot;eacChargeTotal&quot;: 0.0,
                &quot;bdc1Status&quot;: 0,
                &quot;bdc1Mode&quot;: 0,
                &quot;bdc1FaultType&quot;: 0,
                &quot;bdc1WarnCode&quot;: 0,
                &quot;bdc1Vbat&quot;: 0.0,
                &quot;bdc1Ibat&quot;: 0.0,
                &quot;bdc1Soc&quot;: 0,
                &quot;bdc1Vbus1&quot;: 0.0,
                &quot;bdc1Vbus2&quot;: 0.0,
                &quot;bdc1Ibb&quot;: 0.0,
                &quot;bdc1Illc&quot;: 0.0,
                &quot;bdc1Temp1&quot;: 0.0,
                &quot;bdc1Temp2&quot;: 0.0,
                &quot;bdc1DischargePower&quot;: 0.0,
                &quot;bdc1ChargePower&quot;: 0.0,
                &quot;bdc1DischargeTotal&quot;: 0.0,
                &quot;bdc1ChargeTotal&quot;: 0.0,
                &quot;bdc2Status&quot;: 0,
                &quot;bdc2Mode&quot;: 0,
                &quot;bdc2FaultType&quot;: 0,
                &quot;bdc2WarnCode&quot;: 0,
                &quot;bdc2Vbat&quot;: 0.0,
                &quot;bdc2Ibat&quot;: 0.0,
                &quot;bdc2Soc&quot;: 0,
                &quot;bdc2Vbus1&quot;: 0.0,
                &quot;bdc2Vbus2&quot;: 0.0,
                &quot;bdc2Ibb&quot;: 0.0,
                &quot;bdc2Illc&quot;: 0.0,
                &quot;bdc2Temp1&quot;: 0.0,
                &quot;bdc2Temp2&quot;: 0.0,
                &quot;bdc2DischargePower&quot;: 0.0,
                &quot;bdc2ChargePower&quot;: 0.0,
                &quot;bdc2DischargeTotal&quot;: 0.0,
                &quot;bdc2ChargeTotal&quot;: 0.0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsFaultType&quot;: 0,
                &quot;bmsWarnCode&quot;: 0,
                &quot;bmsVbat&quot;: 0.0,
                &quot;bmsIbat&quot;: 0.0,
                &quot;bmsSoc&quot;: 0,
                &quot;bmsTemp1Bat&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsVdelta&quot;: 0.0,
                &quot;bmsIcycle&quot;: 0,
                &quot;bmsSoh&quot;: 0,
                &quot;bmsCvVolt&quot;: 0.0,
                &quot;bmsInfo&quot;: 0.0,
                &quot;bmsPackInfo&quot;: 0.0,
                &quot;bmsUsingCap&quot;: 0.0,
                &quot;bmsFwVersion&quot;: &quot;0&quot;,
                &quot;bmsMcuVersion&quot;: &quot;0&quot;,
                &quot;bmsCommunicationType&quot;: 0,
                &quot;tlxBean&quot;: null,
                &quot;iacr&quot;: 0.0,
                &quot;vacr&quot;: 0.0,
                &quot;pacr&quot;: 0.0,
                &quot;vacrs&quot;: 0.0,
                &quot;operatingMode&quot;: 0,
                &quot;ipv4&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;bdcFaultSubCode&quot;: 0,
                &quot;bdcWarnSubCode&quot;: 0,
                &quot;bdcBusRef&quot;: 0,
                &quot;bdcVbus2Neg&quot;: 0.0,
                &quot;bdcDerateReason&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;bmsError3&quot;: 0,
                &quot;bmsWarn2&quot;: 0,
                &quot;debug1&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;debug2&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;psystem&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;esystemToday&quot;: 0.0,
                &quot;esystemTotal&quot;: 0.0,
                &quot;eselfToday&quot;: 0.0,
                &quot;eselfTotal&quot;: 0.0,
                &quot;batSn&quot;: null,
                &quot;bmsError4&quot;: 0,
                &quot;bmsIosStatus&quot;: 0,
                &quot;pex1&quot;: -0.1,
                &quot;pex2&quot;: -0.1,
                &quot;eex1Today&quot;: -0.1,
                &quot;eex2Today&quot;: -0.1,
                &quot;eex1Total&quot;: -0.1,
                &quot;eex2Total&quot;: -0.1,
                &quot;batteryNo&quot;: -1,
                &quot;batterySN&quot;: null,
                &quot;bsystemWorkMode&quot;: 0,
                &quot;bgridType&quot;: 0,
                &quot;totalWorkingTime&quot;: 0.0,
                &quot;bMerterConnectFlag&quot;: -1,
                &quot;time&quot;: &quot;2024-05-25 14:38:42&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-----  |:-----|----- |
| serialNum | String  | Serial Number  |
| calendar  | Calendar  | Time  |
| withTime  | boolean   | Whether the incoming data includes time  |
| status | int | Min Status 0: waiting, 1: normal, 2: fault  |
| isAgain | boolean  | Is it a retransmission |
| ppv  | String  | Total PV input power |
| ppv1 | String  | PV1 input power  |
| ppv2 | String  | PV2 input power  |
| ppv3 | String  | PV3 input power  |
| pac  | String  | Inverter output power  |
| pacToUserTotal | String | Total power to the grid  |
| pacToGridTotal | String | Total reverse power to the grid  |
| pacToLocalLoad | String | Total load power  |
| timeTotal | Calendar | Total run time  |
| epsPac   | String  | Off-grid output power  |
| vpv1 | String  | PV1 input voltage  |
| ipv1 | String  | PV1 input current  |
| vpv2 | String  | PV2 input voltage  |
| ipv2 | String  | PV2 input current  |
| vpv3 | String  | PV3 input voltage  |
| ipv3 | String  | PV3 input current  |
| fac  | String  | Grid frequency  |
| vac1 | String  | Grid voltage 1  |
| iac1 | String  | Grid current 1  |
| pac1 | String  | Inverter apparent output power 1  |
| vac2 | String  | Grid voltage 2  |
| iac2 | String  | Grid current 2  |
| pac2 | String  | Inverter apparent output power 2  |
| vac3 | String  | Grid voltage 3  |
| iac3 | String  | Grid current 3  |
| pac3 | String  | Inverter apparent output power 3  |
| vacRs | String  | RS line voltage  |
| vacSt | String  | ST line voltage  |
| vacTr | String  | TR line voltage  |
| eacToday | String  | Inverter daily output energy  |
| eacTotal | String | Inverter total output energy  |
| epv1Today| String  | PV1 daily energy generation  |
| epv2Today| String  | PV2 daily energy generation  |
| epv3Today| String  | PV3 daily energy generation  |
| temp1 | String  | Temperature 1  |
| temp2 | String  | Temperature 2  |
| temp3 | String  | Temperature 3  |
| temp4 | String  | Temperature 4  |
| temp5 | String  | Temperature 5  |
| pBusVoltage   | String  | P Bus Voltage  |
| nBusVoltage   | String  | N Bus Voltage  |
| opFullwatt    | String  | Output power limit  |
| invDelayTime  | float  | Grid-tied inverter countdown  |
| pf   | float  | Power factor value  |
| epsPf | float  | Off-grid power factor value  |
| dcVoltage    | float  | DC Voltage  |
| epsFac  | String  | Off-grid frequency   |
| epsVac1 | String  | Off-grid R voltage  |
| epsIac1 | String  | Off-grid R current  |
| epsPac1 | String  | Off-grid R power  |
| epsVac2 | String  | Off-grid S voltage  |
| epsIac2 | String  | Off-grid S current  |
| epsPac2 | String  | Off-grid S power  |
| epsVac3 | String  | Off-grid T voltage  |
| epsIac3 | String  | Off-grid T current  |
| epsPac3 | String  | Off-grid T power  |
| dciR | String  | R phase DC current component  |
| dciS | String  | S phase DC current component  |
| dciT | String  | T phase DC current component  |
| sysFaultWord | int   | 1001  |
| sysFaultWord1 | int  | 1002  |
| sysFaultWord2 | int  | 1003  |
| sysFaultWord3 | int  | 1004  |
| sysFaultWord4 | int  | 1005  |
| sysFaultWord5 | int  | 1006  |
| sysFaultWord6 | int  | 1007  |
| sysFaultWord7 | int  | 1008  |
| faultType   | int  | Fault code  |
| warnCode    | int  | Warning code  |
| realOPPercent | int  | R   |
| deratingMode  | int  | Derating mode  |
| bdcStatus   | int  | BDC connection status  |
| dryContactStatus | int  | Dry contact connection status  |
| loadPercent  | int  | Off-grid load percentage  |
| uwSysWorkMode | int  | System work mode 1000  |
| gfci  | String  | Grid leakage current  |
| iso   | String  | PV insulation resistance  |
| etoUserToday | String  | Daily grid output energy  |
| etoUserTotal | String  | Total grid output energy  |
| etoGridToday | String  | Daily grid input energy  |
| etoGridTotal | String  | Total grid input energy  |
| elocalLoadToday | String  | Daily user load energy consumption  |
| elocalLoadTotal | String  | Total user load energy consumption  |
| epv1Total | String  | PV1 total energy generation  |
| epv2Total | String  | PV2 total energy generation  |
| epv3Total | String  | PV3 total energy generation  |
| epvTotal  | String  | Total PV energy generation  |
| echargeToday | String  | System daily charging energy  |
| echargeTotal | String  | System total charging energy  |
| edischargeToday | String  | System daily discharging energy  |
| edischargeTotal | String  | System total discharging energy  |
| eacChargeToday  | String  | AC daily charging energy  |
| eacChargeTotal  | String  | AC total charging energy  |
| BDC Parameters |  |  |
| bdc1Status	| int  | BDC1 status  |
| bdc1Mode		| int  | BDC1 mode  |
| bdc1FaultType | int  | BDC1 fault code  |
| bdc1WarnCode  | int  | BDC1 warning code  |
| bdc1Vbat		| String  | BDC1 battery voltage  |
| bdc1Ibat		| String  | BDC1 battery current   |
| bdc1Soc		| int  | BDC1 battery capacity  |
| bdc1Vbus1		| String  | BDC1 Bus1 voltage  |
| bdc1Vbus2		| String  | BDC1 Bus2 voltage  |
| bdc1Ibb		| String  | BDC1 BUCK-BOOST Current  |
| bdc1Illc		| String  | BDC1 LLC Current  |
| bdc1Temp1		| String  | BDC1 Temperature A  |
| bdc1Temp2		| String  | BDC1 Temperature B  |
| bdc1DischargePower | String  | BDC1 discharging power  |
| bdc1ChargePower | String  | BDC1 charging power  |
| bdc1DischargeTotal | String  | BDC1 total discharging energy  |
| bdc1ChargeTotal | String  | BDC1 total charging energy  |
| bdc2Status 	  | int  | BDC2 status  |
| bdc2Mode		  | int  | BDC2 mode  |
| bdc2FaultType	  | int  | BDC2 fault code  |
| bdc2WarnCode	  | int  | BDC2 warning code  |
| bdc2Vbat		  | String  | BDC2 battery voltage  |
| bdc2Ibat		  | String  | BDC2 battery current  |
| bdc2Soc		  | int  | BDC2 battery capacity  |
| bdc2Vbus1		  | String  | BDC2 Bus1 voltage  |
| bdc2Vbus2		  | String  | BDC2 Bus2 voltage  |
| bdc2Ibb		  | String  | BDC2 BUCK-BOOST Current  |
| bdc2Illc		  | String  | BDC2 LLC Current  |
| bdc2Temp1		  | String  | BDC2 Temperature A  |
| bdc2Temp2		  | String  | BDC2 Temperature B  |
| bdc2DischargePower | String  | BDC2 discharging power  |
| bdc2ChargePower | String  | BDC2 charging power  |
| bdc2DischargeTotal | String  | BDC2 total discharging energy  |
| bdc2ChargeTotal | String  | BDC2 total charging energy  |
| BMS Parameters |    |    |
| bmsStatus| int  | BMS status  |
| bmsFaultType| int  | BMS fault code  |
| bmsWarnCode| int  | BMS warning code   |
| bmsVbat| String  | BMS battery voltage  |
| bmsIbat| String  | BMS battery current  |
| bmsSoc| String  | BMS battery capacity  |
| bmsTemp1Bat| String  | BMS battery temperature  |
| bmsMaxCurr | String  | BMS maximum current   |
| bmsVdelta  | String  | BMS Delta voltage   |
| bmsIcycle | int  | BMS battery cycle count |
| bmsSoh | int  | BMS battery health index  |
| bmsCvVolt| String  | BMS lithium battery CV voltage |
| bmsInfo | String  | BMS information |
| bmsPackInfo | float  | BMS battery pack information |
| bmsUsingCap | float  | BMS battery capacity |
| bmsFwVersion | String  | BMS internal version |
| bmsMcuVersion | String  | BMS battery MCU version |
| bmsCommunicationType | int  | BMS communication type 0-RS485,1-CAN |
| ipv4 | String  | PV4 input current | 
| vpv4 | String  | PV4 input voltage | 
| ppv4 | String  | PV4 total power | 
| bdcFaultSubCode | String  | BDC fault sub-code | 
| bdcWarnSubCode | String  | BDC warning sub-code | 
| bdcBusRef | String  | BUS soft start flag | 
| bdcVbus2Neg | String  | BDC BUS2Neg voltage | 
| bdcDerateReason | String  | BDC derating reason | 
| bmsError2 | String  | Battery error 2 | 
| bmsError3 | String  | Battery error 3 | 
| bmsError4 | String  | Battery error 4 | 
| bmsWarn2 | String  | Battery warning 2 | 
| debug1 | String  | Debug data 1-8, separated by Chinese characters | 
| debug2 | String  | Debug data 9-16, separated by Chinese characters | 
| psystem | String  | System power generation W, 3019-3020 | 
| pself | String  | Self-consumption power W, 3121-3122 | 
| esystemToday | String  | Daily system energy generation kWh, 3123-3124 | 
| esystemTotal | String  | Total system energy generation kWh, 3137-3138 | 
| eselfToday | String  | Daily self-consumption energy generation kWh, 3139-3140 | 
| eselfTotal | String  | Total self-consumption energy generation kWh, 3141-3142 | 
| bmsIosStatus | String  | Battery ISO detection status, 3210 | 
| pex1 | String  | PV inverter 1 power, 3250-3251 | 
| pex2 | String  | PV inverter 2 power, 3252-3253 | 
| eex1Today | String  | Daily PV inverter 1 output, 3254-3255 | 
| eex2Today | String  | Daily PV inverter 2 output, 3256-3257 | 
| eex1Total | String  | Total PV inverter 1 output, 3258-3259 | 
| eex2Total | String  | Total PV inverter 2 output, 3260-3261 | 
| batteryNo | String  | Battery pack number | 
| batterySN | String  | Battery serial number | 
| epv4Today | String  | PV4 daily energy generation | 
| epv4Total | String  | PV4 total energy generation | 
| operatingMode | String  | Inverter operating mode | 

**Remarks**
- The retrieval frequency is once every 5 minutes or less

---

# 30. min device historical data

*Page ID: `11292926895869382`*

**Brief Description:**

- Data format and parameter description of min device historical data
- `Only applicable: to obtain all detailed data of a device for a specific day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-23&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;AFE494403F&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716550762000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;isAgain&quot;: false,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 1.5,
                &quot;ppv1&quot;: 0.9,
                &quot;ppv2&quot;: 0.6,
                &quot;ppv3&quot;: 0.0,
                &quot;pac&quot;: 1.4,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;pacToLocalLoad&quot;: 1.4,
                &quot;timeTotal&quot;: 1.27918208E7,
                &quot;epsPac&quot;: 0.0,
                &quot;vpv1&quot;: 132.9,
                &quot;ipv1&quot;: 0.0,
                &quot;vpv2&quot;: 125.4,
                &quot;ipv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;fac&quot;: 49.99,
                &quot;vac1&quot;: 224.0,
                &quot;iac1&quot;: 0.3,
                &quot;pac1&quot;: 2.7,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;vacRs&quot;: 224.0,
                &quot;vacSt&quot;: 0.0,
                &quot;vacTr&quot;: 0.0,
                &quot;eacToday&quot;: 7.4,
                &quot;eacTotal&quot;: 25797.8,
                &quot;epv1Today&quot;: 3.8,
                &quot;epv2Today&quot;: 3.6,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;temp1&quot;: 21.9,
                &quot;temp2&quot;: 0.0,
                &quot;temp3&quot;: 0.0,
                &quot;temp4&quot;: 0.0,
                &quot;temp5&quot;: 31.3,
                &quot;pBusVoltage&quot;: 358.4,
                &quot;nBusVoltage&quot;: 0.0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;invDelayTime&quot;: 0.0,
                &quot;pf&quot;: 1.0,
                &quot;epsPf&quot;: -1.0,
                &quot;dcVoltage&quot;: 0.0,
                &quot;epsFac&quot;: 0.0,
                &quot;epsVac1&quot;: 0.0,
                &quot;epsIac1&quot;: 0.0,
                &quot;epsPac1&quot;: 0.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;epsPac2&quot;: 0.0,
                &quot;epsVac3&quot;: 0.0,
                &quot;epsIac3&quot;: 0.0,
                &quot;epsPac3&quot;: 0.0,
                &quot;dciR&quot;: 5.0,
                &quot;dciS&quot;: 0.0,
                &quot;dciT&quot;: 0.0,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;faultType&quot;: 0,
                &quot;faultType1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;deratingMode&quot;: 0,
                &quot;bdcStatus&quot;: 0,
                &quot;dryContactStatus&quot;: 0,
                &quot;loadPercent&quot;: 0.0,
                &quot;uwSysWorkMode&quot;: 0,
                &quot;gfci&quot;: 5193,
                &quot;iso&quot;: 2798,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 0.0,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;epv1Total&quot;: 13629.1,
                &quot;epv2Total&quot;: 12370.8,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epvTotal&quot;: 25999.9,
                &quot;echargeToday&quot;: 0.0,
                &quot;echargeTotal&quot;: 0.0,
                &quot;edischargeToday&quot;: 0.0,
                &quot;edischargeTotal&quot;: 0.0,
                &quot;eacChargeToday&quot;: 0.0,
                &quot;eacChargeTotal&quot;: 0.0,
                &quot;bdc1Status&quot;: 0,
                &quot;bdc1Mode&quot;: 0,
                &quot;bdc1FaultType&quot;: 0,
                &quot;bdc1WarnCode&quot;: 0,
                &quot;bdc1Vbat&quot;: 0.0,
                &quot;bdc1Ibat&quot;: 0.0,
                &quot;bdc1Soc&quot;: 0,
                &quot;bdc1Vbus1&quot;: 0.0,
                &quot;bdc1Vbus2&quot;: 0.0,
                &quot;bdc1Ibb&quot;: 0.0,
                &quot;bdc1Illc&quot;: 0.0,
                &quot;bdc1Temp1&quot;: 0.0,
                &quot;bdc1Temp2&quot;: 0.0,
                &quot;bdc1DischargePower&quot;: 0.0,
                &quot;bdc1ChargePower&quot;: 0.0,
                &quot;bdc1DischargeTotal&quot;: 0.0,
                &quot;bdc1ChargeTotal&quot;: 0.0,
                &quot;bdc2Status&quot;: 0,
                &quot;bdc2Mode&quot;: 0,
                &quot;bdc2FaultType&quot;: 0,
                &quot;bdc2WarnCode&quot;: 0,
                &quot;bdc2Vbat&quot;: 0.0,
                &quot;bdc2Ibat&quot;: 0.0,
                &quot;bdc2Soc&quot;: 0,
                &quot;bdc2Vbus1&quot;: 0.0,
                &quot;bdc2Vbus2&quot;: 0.0,
                &quot;bdc2Ibb&quot;: 0.0,
                &quot;bdc2Illc&quot;: 0.0,
                &quot;bdc2Temp1&quot;: 0.0,
                &quot;bdc2Temp2&quot;: 0.0,
                &quot;bdc2DischargePower&quot;: 0.0,
                &quot;bdc2ChargePower&quot;: 0.0,
                &quot;bdc2DischargeTotal&quot;: 0.0,
                &quot;bdc2ChargeTotal&quot;: 0.0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsFaultType&quot;: 0,
                &quot;bmsWarnCode&quot;: 0,
                &quot;bmsVbat&quot;: 0.0,
                &quot;bmsIbat&quot;: 0.0,
                &quot;bmsSoc&quot;: 0,
                &quot;bmsTemp1Bat&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsVdelta&quot;: 0.0,
                &quot;bmsIcycle&quot;: 0,
                &quot;bmsSoh&quot;: 0,
                &quot;bmsCvVolt&quot;: 0.0,
                &quot;bmsInfo&quot;: 0.0,
                &quot;bmsPackInfo&quot;: 0.0,
                &quot;bmsUsingCap&quot;: 0.0,
                &quot;bmsFwVersion&quot;: &quot;0&quot;,
                &quot;bmsMcuVersion&quot;: &quot;0&quot;,
                &quot;bmsCommunicationType&quot;: 0,
                &quot;tlxBean&quot;: null,
                &quot;iacr&quot;: 0.0,
                &quot;vacr&quot;: 0.0,
                &quot;pacr&quot;: 0.0,
                &quot;vacrs&quot;: 0.0,
                &quot;operatingMode&quot;: 0,
                &quot;ipv4&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;bdcFaultSubCode&quot;: 0,
                &quot;bdcWarnSubCode&quot;: 0,
                &quot;bdcBusRef&quot;: 0,
                &quot;bdcVbus2Neg&quot;: 0.0,
                &quot;bdcDerateReason&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;bmsError3&quot;: 0,
                &quot;bmsWarn2&quot;: 0,
                &quot;debug1&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;debug2&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;psystem&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;esystemToday&quot;: 0.0,
                &quot;esystemTotal&quot;: 0.0,
                &quot;eselfToday&quot;: 0.0,
                &quot;eselfTotal&quot;: 0.0,
                &quot;batSn&quot;: null,
                &quot;bmsError4&quot;: 0,
                &quot;bmsIosStatus&quot;: 0,
                &quot;pex1&quot;: -0.1,
                &quot;pex2&quot;: -0.1,
                &quot;eex1Today&quot;: -0.1,
                &quot;eex2Today&quot;: -0.1,
                &quot;eex1Total&quot;: -0.1,
                &quot;eex2Total&quot;: -0.1,
                &quot;batteryNo&quot;: -1,
                &quot;batterySN&quot;: null,
                &quot;bsystemWorkMode&quot;: 0,
                &quot;bgridType&quot;: 0,
                &quot;totalWorkingTime&quot;: 0.0,
                &quot;bMerterConnectFlag&quot;: 0,
                &quot;time&quot;: &quot;2024-05-24 19:39:22&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;
            },
			{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-23&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;AFE494403F&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;alias&quot;: null,
                &quot;address&quot;: 0,
                &quot;calendar&quot;: 1716550762000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;isAgain&quot;: false,
                &quot;lost&quot;: true,
                &quot;day&quot;: null,
                &quot;ppv&quot;: 1.5,
                &quot;ppv1&quot;: 0.9,
                &quot;ppv2&quot;: 0.6,
                &quot;ppv3&quot;: 0.0,
                &quot;pac&quot;: 1.4,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;pacToLocalLoad&quot;: 1.4,
                &quot;timeTotal&quot;: 1.27918208E7,
                &quot;epsPac&quot;: 0.0,
                &quot;vpv1&quot;: 132.9,
                &quot;ipv1&quot;: 0.0,
                &quot;vpv2&quot;: 125.4,
                &quot;ipv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;fac&quot;: 49.99,
                &quot;vac1&quot;: 224.0,
                &quot;iac1&quot;: 0.3,
                &quot;pac1&quot;: 2.7,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;vacRs&quot;: 224.0,
                &quot;vacSt&quot;: 0.0,
                &quot;vacTr&quot;: 0.0,
                &quot;eacToday&quot;: 7.4,
                &quot;eacTotal&quot;: 25797.8,
                &quot;epv1Today&quot;: 3.8,
                &quot;epv2Today&quot;: 3.6,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;temp1&quot;: 21.9,
                &quot;temp2&quot;: 0.0,
                &quot;temp3&quot;: 0.0,
                &quot;temp4&quot;: 0.0,
                &quot;temp5&quot;: 31.3,
                &quot;pBusVoltage&quot;: 358.4,
                &quot;nBusVoltage&quot;: 0.0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;invDelayTime&quot;: 0.0,
                &quot;pf&quot;: 1.0,
                &quot;epsPf&quot;: -1.0,
                &quot;dcVoltage&quot;: 0.0,
                &quot;epsFac&quot;: 0.0,
                &quot;epsVac1&quot;: 0.0,
                &quot;epsIac1&quot;: 0.0,
                &quot;epsPac1&quot;: 0.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;epsPac2&quot;: 0.0,
                &quot;epsVac3&quot;: 0.0,
                &quot;epsIac3&quot;: 0.0,
                &quot;epsPac3&quot;: 0.0,
                &quot;dciR&quot;: 5.0,
                &quot;dciS&quot;: 0.0,
                &quot;dciT&quot;: 0.0,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;faultType&quot;: 0,
                &quot;faultType1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;realOPPercent&quot;: 0,
                &quot;deratingMode&quot;: 0,
                &quot;bdcStatus&quot;: 0,
                &quot;dryContactStatus&quot;: 0,
                &quot;loadPercent&quot;: 0.0,
                &quot;uwSysWorkMode&quot;: 0,
                &quot;gfci&quot;: 5193,
                &quot;iso&quot;: 2798,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 0.0,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;epv1Total&quot;: 13629.1,
                &quot;epv2Total&quot;: 12370.8,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epvTotal&quot;: 25999.9,
                &quot;echargeToday&quot;: 0.0,
                &quot;echargeTotal&quot;: 0.0,
                &quot;edischargeToday&quot;: 0.0,
                &quot;edischargeTotal&quot;: 0.0,
                &quot;eacChargeToday&quot;: 0.0,
                &quot;eacChargeTotal&quot;: 0.0,
                &quot;bdc1Status&quot;: 0,
                &quot;bdc1Mode&quot;: 0,
                &quot;bdc1FaultType&quot;: 0,
                &quot;bdc1WarnCode&quot;: 0,
                &quot;bdc1Vbat&quot;: 0.0,
                &quot;bdc1Ibat&quot;: 0.0,
                &quot;bdc1Soc&quot;: 0,
                &quot;bdc1Vbus1&quot;: 0.0,
                &quot;bdc1Vbus2&quot;: 0.0,
                &quot;bdc1Ibb&quot;: 0.0,
                &quot;bdc1Illc&quot;: 0.0,
                &quot;bdc1Temp1&quot;: 0.0,
                &quot;bdc1Temp2&quot;: 0.0,
                &quot;bdc1DischargePower&quot;: 0.0,
                &quot;bdc1ChargePower&quot;: 0.0,
                &quot;bdc1DischargeTotal&quot;: 0.0,
                &quot;bdc1ChargeTotal&quot;: 0.0,
                &quot;bdc2Status&quot;: 0,
                &quot;bdc2Mode&quot;: 0,
                &quot;bdc2FaultType&quot;: 0,
                &quot;bdc2WarnCode&quot;: 0,
                &quot;bdc2Vbat&quot;: 0.0,
                &quot;bdc2Ibat&quot;: 0.0,
                &quot;bdc2Soc&quot;: 0,
                &quot;bdc2Vbus1&quot;: 0.0,
                &quot;bdc2Vbus2&quot;: 0.0,
                &quot;bdc2Ibb&quot;: 0.0,
                &quot;bdc2Illc&quot;: 0.0,
                &quot;bdc2Temp1&quot;: 0.0,
                &quot;bdc2Temp2&quot;: 0.0,
                &quot;bdc2DischargePower&quot;: 0.0,
                &quot;bdc2ChargePower&quot;: 0.0,
                &quot;bdc2DischargeTotal&quot;: 0.0,
                &quot;bdc2ChargeTotal&quot;: 0.0,
                &quot;bmsStatus&quot;: 0,
                &quot;bmsFaultType&quot;: 0,
                &quot;bmsWarnCode&quot;: 0,
                &quot;bmsVbat&quot;: 0.0,
                &quot;bmsIbat&quot;: 0.0,
                &quot;bmsSoc&quot;: 0,
                &quot;bmsTemp1Bat&quot;: 0.0,
                &quot;bmsMaxCurr&quot;: 0.0,
                &quot;bmsVdelta&quot;: 0.0,
                &quot;bmsIcycle&quot;: 0,
                &quot;bmsSoh&quot;: 0,
                &quot;bmsCvVolt&quot;: 0.0,
                &quot;bmsInfo&quot;: 0.0,
                &quot;bmsPackInfo&quot;: 0.0,
                &quot;bmsUsingCap&quot;: 0.0,
                &quot;bmsFwVersion&quot;: &quot;0&quot;,
                &quot;bmsMcuVersion&quot;: &quot;0&quot;,
                &quot;bmsCommunicationType&quot;: 0,
                &quot;tlxBean&quot;: null,
                &quot;iacr&quot;: 0.0,
                &quot;vacr&quot;: 0.0,
                &quot;pacr&quot;: 0.0,
                &quot;vacrs&quot;: 0.0,
                &quot;operatingMode&quot;: 0,
                &quot;ipv4&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;bdcFaultSubCode&quot;: 0,
                &quot;bdcWarnSubCode&quot;: 0,
                &quot;bdcBusRef&quot;: 0,
                &quot;bdcVbus2Neg&quot;: 0.0,
                &quot;bdcDerateReason&quot;: 0,
                &quot;bmsError2&quot;: 0,
                &quot;bmsError3&quot;: 0,
                &quot;bmsWarn2&quot;: 0,
                &quot;debug1&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;debug2&quot;: &quot;0，0，0，0，0，0，0，0&quot;,
                &quot;psystem&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;esystemToday&quot;: 0.0,
                &quot;esystemTotal&quot;: 0.0,
                &quot;eselfToday&quot;: 0.0,
                &quot;eselfTotal&quot;: 0.0,
                &quot;batSn&quot;: null,
                &quot;bmsError4&quot;: 0,
                &quot;bmsIosStatus&quot;: 0,
                &quot;pex1&quot;: -0.1,
                &quot;pex2&quot;: -0.1,
                &quot;eex1Today&quot;: -0.1,
                &quot;eex2Today&quot;: -0.1,
                &quot;eex1Total&quot;: -0.1,
                &quot;eex2Total&quot;: -0.1,
                &quot;batteryNo&quot;: -1,
                &quot;batterySN&quot;: null,
                &quot;bsystemWorkMode&quot;: 0,
                &quot;bgridType&quot;: 0,
                &quot;totalWorkingTime&quot;: 0.0,
                &quot;bMerterConnectFlag&quot;: 0,
                &quot;time&quot;: &quot;2024-05-24 19:39:22&quot;,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Normal&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;
            }, ],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
			
```

 **Return Parameter Description**

|Parameter Name|Type|Description|
|:-----  |:-----|----- |
| serialNum | String  | Serial Number  |
| calendar  | Calendar  | Time  |
| withTime  | boolean   | Whether the incoming data includes time  |
| status | int | Tlx Status 0: waiting, 1: normal, 2: fault  |
| isAgain | boolean  | Is it a retransmission |
| ppv  | String  | Total PV input power |
| ppv1 | String  | PV1 input power  |
| ppv2 | String  | PV2 input power  |
| ppv3 | String  | PV3 input power  |
| pac  | String  | Inverter output power  |
| pacToUserTotal | String | Total power flowing to the grid  |
| pacToGridTotal | String | Total power flowing back to the grid  |
| pacToLocalLoad | String | Total load power  |
| timeTotal | double | Total runtime  |
| epsPac   | String  | Off-grid output power  |
| vpv1 | String  | PV1 input voltage  |
| ipv1 | String  | PV1 input current  |
| vpv2 | String  | PV2 input voltage  |
| ipv2 | String  | PV2 input current  |
| vpv3 | String  | PV3 input voltage  |
| ipv3 | String  | PV3 input current  |
| fac  | String  | Grid frequency  |
| vac1 | String  | Grid voltage 1  |
| iac1 | String  | Grid current 1  |
| pac1 | String  | Inverter apparent power output 1  |
| vac2 | String  | Grid voltage 2  |
| iac2 | String  | Grid current 2  |
| pac2 | String  | Inverter apparent power output 2  |
| vac3 | String  | Grid voltage 3  |
| iac3 | String  | Grid current 3  |
| pac3 | String  | Inverter apparent power output 3  |
| vacRs | String  | RS line voltage  |
| vacSt | String  | ST line voltage  |
| vacTr | String  | TR line voltage  |
| eacToday | String  | Daily inverter output energy  |
| eacTotal | String | Total inverter output energy  |
| epv1Today| String  | Daily PV1 generation  |
| epv2Today| String  | Daily PV2 generation  |
| epv3Today| String  | Daily PV3 generation  |
| temp1 | String  | Temperature 1  |
| temp2 | String  | Temperature 2  |
| temp3 | String  | Temperature 3  |
| temp4 | String  | Temperature 4  |
| temp5 | String  | Temperature 5  |
| pBusVoltage   | String  | P Bus Voltage  |
| nBusVoltage   | String  | N Bus Voltage  |
| opFullwatt    | String  | Output Power Limit  |
| invDelayTime  | float  | Grid-tied inverter countdown  |
| pf   | float  | pf value  |
| epsPf | float  | Off-grid pf value  |
| dcVoltage    | float  | DC Voltage  |
| epsFac  | String  | Off-grid frequency   |
| epsVac1 | String  | Off-grid R voltage  |
| epsIac1 | String  | Off-grid R current  |
| epsPac1 | String  | Off-grid R power  |
| epsVac2 | String  | Off-grid S voltage  |
| epsIac2 | String  | Off-grid S current  |
| epsPac2 | String  | Off-grid S power  |
| epsVac3 | String  | Off-grid T voltage  |
| epsIac3 | String  | Off-grid T current  |
| epsPac3 | String  | Off-grid T power  |
| dciR | String  | DC current component of R phase  |
| dciS | String  | DC current component of S phase  |
| dciT | String  | DC current component of T phase  |
| sysFaultWord | int   | 1001  |
| sysFaultWord1 | int  | 1002  |
| sysFaultWord2 | int  | 1003  |
| sysFaultWord3 | int  | 1004  |
| sysFaultWord4 | int  | 1005  |
| sysFaultWord5 | int  | 1006  |
| sysFaultWord6 | int  | 1007  |
| sysFaultWord7 | int  | 1008  |
| faultType   | int  | Fault code  |
| warnCode    | int  | Warning code  |
| realOPPercent | int  | R   |
| deratingMode  | int  | Derating mode  |
| bdcStatus   | int  | BDC connection status  |
| dryContactStatus | int  | Dry contact connection status  |
| loadPercent  | int  | Off-grid load percentage  |
| uwSysWorkMode | int  | System working mode 1000  |
| gfci  | int  | Grid leakage current  |
| iso   | int  | PV insulation resistance  |
| etoUserToday | String  | Daily grid output energy  |
| etoUserTotal | String  | Total grid output energy  |
| etoGridToday | String  | Daily grid input energy  |
| etoGridTotal | String  | Total grid input energy  |
| elocalLoadToday | String  | Daily user load energy consumption  |
| elocalLoadTotal | String  | Total user load energy consumption  |
| epv1Total | String  | Total PV1 generation  |
| epv2Total | String  | Total PV2 generation  |
| epv3Total | String  | Total PV3 generation  |
| epvTotal  | String  | Total PV generation  |
| echargeToday | String  | Daily system charging energy  |
| echargeTotal | String  | Total system charging energy  |
| edischargeToday | String  | Daily system discharging energy  |
| edischargeTotal | String  | Total system discharging energy  |
| eacChargeToday  | String  | Daily AC charging energy  |
| eacChargeTotal  | String  | Total AC charging energy  |
| BDC Parameters |  |  |
| bdc1Status	| int  | BDC1 status  |
| bdc1Mode		| int  | BDC1 mode  |
| bdc1FaultType | int  | BDC1 fault code  |
| bdc1WarnCode  | int  | BDC1 warning code  |
| bdc1Vbat		| String  | BDC1 battery voltage  |
| bdc1Ibat		| String  | BDC1 battery current   |
| bdc1Soc		| int  | BDC1 battery capacity  |
| bdc1Vbus1		| String  | BDC1 Bus1 voltage  |
| bdc1Vbus2		| String  | BDC1 Bus2 voltage  |
| bdc1Ibb		| String  | BDC1 BUCK-BOOST Current  |
| bdc1Illc		| String  | BDC1 LLC Current  |
| bdc1Temp1		| String  | BDC1 Temperature A  |
| bdc1Temp2		| String  | BDC1 Temperature B  |
| bdc1DischargePower | String  | BDC1 discharge power  |
| bdc1ChargePower | String  | BDC1 charge power  |
| bdc1DischargeTotal | String  | BDC1 total discharge energy  |
| bdc1ChargeTotal | String  | BDC1 total charge energy  |
| bdc2Status 	  | int  | BDC2 status  |
| bdc2Mode		  | int  | BDC2 mode  |
| bdc2FaultType	  | int  | BDC2 fault code  |
| bdc2WarnCode	  | int  | BDC2 warning code  |
| bdc2Vbat		  | String  | BDC2 battery voltage  |
| bdc2Ibat		  | String  | BDC2 battery current  |
| bdc2Soc		  | int  | BDC2 battery capacity  |
| bdc2Vbus1		  | String  | BDC2 Bus1 voltage  |
| bdc2Vbus2		  | String  | BDC2 Bus2 voltage  |
| bdc2Ibb		  | String  | BDC2 BUCK-BOOST Current  |
| bdc2Illc		  | String  | BDC2 LLC Current  |
| bdc2Temp1		  | String  | BDC2 Temperature A  |
| bdc2Temp2		  | String  | BDC2 Temperature B  |
| bdc2DischargePower | String  | BDC2 discharge power  |
| bdc2ChargePower | String  | BDC2 charge power  |
| bdc2DischargeTotal | String  | BDC2 total discharge energy  |
| bdc2ChargeTotal | String  | BDC2 total charge energy  |
| BMS Parameters |    |    |
| bmsStatus| int  | BMS status  |
| bmsFaultType| int  | BMS fault code  |
| bmsWarnCode| int  | BMS warning code   |
| bmsVbat| String  | BMS battery voltage  |
| bmsIbat| String  | BMS battery current  |
| bmsSoc| int  | BMS battery capacity  |
| bmsTemp1Bat| String  | BMS battery temperature  |
| bmsMaxCurr | String  | BMS maximum current   |
| bmsVdelta  | String  | BMS Delta voltage   |
| bmsIcycle | int  | BMS battery cycle count |
| bmsSoh | int  | BMS battery health index  |
| bmsCvVolt| float  | BMS lithium battery CV voltage |
| bmsInfo | float  | BMS information |
| bmsPackInfo | float  | BMS battery pack information |
| bmsUsingCap | float  | BMS battery capacity |
| bmsFwVersion | String  | BMS firmware version |
| bmsMcuVersion | String  | BMS battery MCU version |
| bmsCommunicationType | int  | BMS communication type 0-RS485, 1-CAN |
| ipv4 | String  | PV4 input current | 
| vpv4 | String  | PV4 input voltage | 
| ppv4 | String  | PV4 input total power | 
| bdcFaultSubCode | String  | BDC fault sub-code | 
| bdcWarnSubCode | String  | BDC warning sub-code | 
| bdcBusRef | String  | BUS soft start flag | 
| bdcVbus2Neg | String  | BDC BUS2Neg voltage | 
| bdcDerateReason | String  | BDC derating reason | 
| bmsError2 | String  | Battery error 2 | 
| bmsError3 | String  | Battery error 3 | 
| bmsError4 | String  | Battery error 4 | 
| bmsWarn2 | String  | Battery warning 2 | 
| debug1 | String  |  Debug data 1-8, separated by Chinese characters | 
| debug2 | String  |  Debug data 9-16, separated by Chinese characters | 
| psystem | String  | System generation power W, 3019-3020 | 
| pself | String  | Self-generation power W, 3121-3122 | 
| esystemToday | String  | Daily system generation kWh, 3123-3124 | 
| esystemTotal | String  | Total system generation kWh, 3137-3138 | 
| eselfToday | String  | Daily self-generation kWh, 3139-3140 | 
| eselfTotal | String  | Total self-generation kWh, 3141-3142 | 
| bmsIosStatus | String  | Battery ISO detection status, 3210 | 
| pex1 | String  | PV inverter 1 power, 3250-3251 | 
| pex2 | String  | PV inverter 2 power, 3252-3253 | 
| eex1Today | String  |  Today's PV inverter 1 output, 3254-3255 | 
| eex2Today | String  |  Today's PV inverter 2 output, 3256-3257 | 
| eex1Total | String  | Total PV inverter 1 output, 3258-3259 | 
| eex2Total | String  | Total PV inverter 2 output, 3260-3261 | 
| batteryNo | String  | Battery pack number | 
| batterySN | String  | Battery serial number | 
| epv4Today | String  | Daily PV4 generation | 
| epv4Total | String  | Total PV4 generation | 
| operatingMode | String  |  Inverter operating mode | 


 **Notes** 
- Frequency of acquisition is once every 5 minutes


---

# 31. wit basic information

*Page ID: `11292927244927496`*

  
**Brief Description:**

- The data return format for the basic information of wit devices and the explanation of some parameters of the basic information.
- `Only applicable to: Batch retrieval of device basic information.`



**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;wit&quot;: [
            {
                &quot;id&quot;: 0,
                &quot;serialNum&quot;: &quot;0ZFN00R23ZBF0002&quot;,
                &quot;portName&quot;: &quot;ShinePano - TTN0D9E01P&quot;,
                &quot;dataLogSn&quot;: &quot;TTN0D9E01P&quot;,
                &quot;sysTime&quot;: &quot;2024-05-29 14:00:25&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;0ZFN00R23ZBF0002&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;lost&quot;: false,
                &quot;lastUpdateTime&quot;: 1716963248000,
                &quot;tcpServerIp&quot;: &quot;120.25.191.20&quot;,
                &quot;status&quot;: 1,
                &quot;addr&quot;: 5,
                &quot;deviceType&quot;: 218,
                &quot;onOff&quot;: 1,
                &quot;saftyFunc&quot;: 0,
                &quot;pvPfCmdMemoryState&quot;: 0,
                &quot;activeRate&quot;: 50,
                &quot;reactiveRate&quot;: 0,
                &quot;powerFactor&quot;: 1.0,
                &quot;pmax&quot;: 100000,
                &quot;vnormal&quot;: 2.0,
                &quot;fwVersion&quot;: &quot;TO1.0&quot;,
                &quot;model&quot;: 2377905207708287976,
                &quot;comName&quot;: &quot;null&quot;,
                &quot;comVersion&quot;: &quot;ZBea-0037&quot;,
                &quot;lcdLanguage&quot;: 1,
                &quot;countrySelected&quot;: 1,
                &quot;vpvStart&quot;: 250.0,
                &quot;timeStart&quot;: 30,
                &quot;restartTime&quot;: 10,
                &quot;wPowerStartSlope&quot;: 50.0,
                &quot;wPowerRestartSlopeEE&quot;: 50.0,
                &quot;wselectBaudrate&quot;: 0,
                &quot;comAddress&quot;: 2,
                &quot;dtc&quot;: 5600,
                &quot;vacLow&quot;: 276.0,
                &quot;vacHigh&quot;: 458.1,
                &quot;facLow&quot;: 475.0,
                &quot;facHigh&quot;: 525.0,
                &quot;voltageHighLimit&quot;: 456.4,
                &quot;voltageLowLimit&quot;: 277.7,
                &quot;freqHighLimit&quot;: 50.5,
                &quot;freqLowLimit&quot;: 47.5,
                &quot;version&quot;: &quot;TOaa181390&quot;,
                &quot;modbusVersion&quot;: 305,
                &quot;pfModel&quot;: 0,
                &quot;module4&quot;: 0,
                &quot;module3&quot;: 0,
                &quot;module2&quot;: 0,
                &quot;module1&quot;: 0,
                &quot;uwAntiBackflow&quot;: 0,
                &quot;wAntiBackflowMeterPowerLimit&quot;: 0.0,
                &quot;reactiveValue&quot;: 0.0,
                &quot;reactiveOutputPriority&quot;: 0,
                &quot;uwOnOffChangeMode&quot;: 0,
                &quot;uwPcsType&quot;: 1,
                &quot;uwACChargePowerRate&quot;: 100,
                &quot;uwBattMaxChargeVol&quot;: 854.0,
                &quot;uwBattEODVol&quot;: 678.0,
                &quot;uwConnectPhaseMode&quot;: 0,
                &quot;uwDisConnectPhaseMode&quot;: 0,
                &quot;uwBatMaxChargeCurrent&quot;: 140.0,
                &quot;uwBatMaxDisChargeCurrent&quot;: 140.0,
                &quot;uwOnOffChangeManualMode&quot;: 1,
                &quot;uwOnOffGridSet&quot;: 0,
                &quot;uwOffGridVol&quot;: 1.0,
                &quot;uwOffGridFreq&quot;: 0.0,
                &quot;uwLoadPvInverter&quot;: 0,
                &quot;uwACChargeEnable&quot;: 1,
                &quot;uwOffGridEnable&quot;: 1,
                &quot;uwBatChargeStopSoc&quot;: 100,
                &quot;uwBatDisChargeStopSoc&quot;: 10,
                &quot;singleExport&quot;: 0,
                &quot;forcedTimeStart1&quot;: &quot;21:0&quot;,
                &quot;forcedTimeStart2&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStart3&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStart4&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStart5&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStart6&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStop1&quot;: &quot;22:0&quot;,
                &quot;forcedTimeStop2&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStop3&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStop4&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStop5&quot;: &quot;0:0&quot;,
                &quot;forcedTimeStop6&quot;: &quot;0:0&quot;,
                &quot;time1Mode&quot;: 0,
                &quot;time2Mode&quot;: 0,
                &quot;time3Mode&quot;: 0,
                &quot;time4Mode&quot;: 0,
                &quot;time5Mode&quot;: 0,
                &quot;time6Mode&quot;: 0,
                &quot;forcedStopSwitch1&quot;: 0,
                &quot;forcedStopSwitch2&quot;: 0,
                &quot;forcedStopSwitch3&quot;: 0,
                &quot;forcedStopSwitch4&quot;: 0,
                &quot;forcedStopSwitch5&quot;: 0,
                &quot;forcedStopSwitch6&quot;: 0,
                &quot;pflinep1_lp&quot;: 0,
                &quot;pflinep1_pf&quot;: -1.0,
                &quot;pflinep2_lp&quot;: 0,
                &quot;pflinep2_pf&quot;: -1.0,
                &quot;pflinep3_lp&quot;: 0,
                &quot;pflinep3_pf&quot;: -1.0,
                &quot;pflinep4_lp&quot;: 0,
                &quot;pflinep4_pf&quot;: -1.0,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;energyMonth&quot;: 0.0,
                &quot;energyDayMap&quot;: {},
                &quot;userName&quot;: null,
                &quot;modelText&quot;: &quot;S21B00D04T30P0FU01M03E8&quot;,
                &quot;plantId&quot;: 0,
                &quot;plantName&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;sysTimeText&quot;: &quot;2024-05-29 14:00:25&quot;,
                &quot;uwGenPortDevType&quot;: 0,
                &quot;uwGenPower&quot;: 0.0,
                &quot;oilEnable&quot;: 0,
                &quot;uwDgStartSoc&quot;: 20,
                &quot;uwDgStopSoc&quot;: 30,
                &quot;uwBattType1&quot;: 0,
                &quot;uwBattType2&quot;: 0,
                &quot;uwBattType3&quot;: 0,
                &quot;uwBatCap&quot;: 100,
                &quot;uw2thBatMaxChgVol&quot;: 1000.0,
                &quot;uw2thBatEndOfVol&quot;: 1000.0,
                &quot;uw2thBatMaxChgCurr&quot;: 1000.0,
                &quot;uw2thBatMaxDisChgCurr&quot;: 1000.0,
                &quot;uw2thBatCap&quot;: 10000,
                &quot;uw2thBatChgLimit&quot;: 1000.0,
                &quot;uw2thBatDisChgLimit&quot;: 1000.0,
                &quot;uw3thBatMaxChgVol&quot;: 1000.0,
                &quot;uw3thBatEndOfVol&quot;: 1000.0,
                &quot;uw3thBatMaxChgCurr&quot;: 1000.0,
                &quot;uw3thBatMaxDisChgCurr&quot;: 1000.0,
                &quot;uw3thBatCap&quot;: 10000,
                &quot;uw3thBatChgLimit&quot;: 1000.0,
                &quot;uw3thBatDisChgLimit&quot;: 1000.0,
                &quot;uwBatCnnWay&quot;: 10000,
                &quot;uwACoupleEnable&quot;: 0,
                &quot;uwACoupleStartSOC&quot;: 0,
                &quot;uwACoupleEndSOC&quot;: 0,
                &quot;uw1thBatChgLimit&quot;: 0.0,
                &quot;uw1thBatDisChgLimit&quot;: 0.1,
                &quot;uwBatEnable1&quot;: 0,
                &quot;uwBatEnable2&quot;: 0,
                &quot;uwBatEnable3&quot;: 0,
                &quot;batSerialNum1&quot;: &quot;0WZN00R23ZB0000C&quot;,
                &quot;batSerialNum2&quot;: &quot;&quot;,
                &quot;batSerialNum3&quot;: &quot;&quot;,
                &quot;batSerialNum4&quot;: &quot;&quot;,
                &quot;batSerialNum5&quot;: &quot;,bdcLinkNum=1,packNum=13&quot;,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;,
                &quot;treeName&quot;: &quot;0ZFN00R23ZBF0002&quot;,
                &quot;treeID&quot;: &quot;ST_0ZFN00R23ZBF0002&quot;,
                &quot;parentID&quot;: &quot;LIST_TTN0D9E01P_218&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;antiBackflowFlag&quot;: 0,
                &quot;svgFunction&quot;: 0,
                &quot;statusText&quot;: &quot;wit.status.operating&quot;,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-29 14:14:08&quot;,
                &quot;level&quot;: 4,
                &quot;children&quot;: null
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-----|:-----|-----|
| serialNum | string | Device Serial Number |
| lost | string | Device Online Status (0: Online, 1: Offline) |
| status | int | Device Status (0: Offline, 1: Online, 2: Standby, 3: Fault, others: Disconnected) |
| alias | int | Alias |
| location | string | Address |
| dataLogSn | string | Data Logger Serial Number |
| nominalPower | string | Nominal Power |
| power | string | Current Power |
| eToday | string | Today's Energy Generation |
| eTotal | string | Total Energy Generation |
| lastUpdateTime | string | Last Update Time |
| tcpServerIp | string | Server Address |
| fwVersion | string | Inverter Firmware Version |

**Notes**
- The data is retrieved up to once every 5 minutes.


---

# 32. The last detailed data of wit.

*Page ID: `11292928051977434`*

**Brief Description:**

- Data format and parameter description of the last detailed data of the WIT device.

- `Only applicable for: bulk retrieval of the last data of devices.`


**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;wit&quot;: [
            {
                &quot;serialNum&quot;: &quot;QWL0DC3002&quot;,
                &quot;dataLogSn&quot;: &quot;XGD6E452V7&quot;,
                &quot;calendar&quot;: 1716965658551,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;ppv&quot;: 0.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;ppv5&quot;: 0.0,
                &quot;ppv6&quot;: 0.0,
                &quot;ppv7&quot;: 0.0,
                &quot;ppv8&quot;: 0.0,
                &quot;vpv1&quot;: 1.3,
                &quot;vpv2&quot;: 92.4,
                &quot;vpv3&quot;: 94.2,
                &quot;vpv4&quot;: 90.7,
                &quot;vpv5&quot;: 93.9,
                &quot;vpv6&quot;: 94.0,
                &quot;vpv7&quot;: 93.3,
                &quot;vpv8&quot;: 93.8,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;ipv4&quot;: 0.0,
                &quot;ipv5&quot;: 0.0,
                &quot;ipv6&quot;: 0.0,
                &quot;ipv7&quot;: 0.0,
                &quot;ipv8&quot;: 0.0,
                &quot;pac&quot;: 0.0,
                &quot;fac&quot;: 49.98,
                &quot;vac1&quot;: 222.8,
                &quot;iac1&quot;: 5.0,
                &quot;pac1&quot;: 1119.5,
                &quot;vac2&quot;: 223.1,
                &quot;iac2&quot;: 5.5,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;eacToday&quot;: 0.0,
                &quot;eacTotal&quot;: 0.0,
                &quot;timeTotal&quot;: 0.0,
                &quot;epv1Today&quot;: 0.0,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epv5Today&quot;: 0.0,
                &quot;epv5Total&quot;: 0.0,
                &quot;epv6Today&quot;: 0.0,
                &quot;epv6Total&quot;: 0.0,
                &quot;epv7Today&quot;: 0.0,
                &quot;epv7Total&quot;: 0.0,
                &quot;epv8Today&quot;: 0.0,
                &quot;epv8Total&quot;: 0.0,
                &quot;epvToday&quot;: 0.0,
                &quot;epvTotal&quot;: 0.0,
                &quot;temp1&quot;: 0.0,
                &quot;temp2&quot;: 0.0,
                &quot;temp3&quot;: 0.0,
                &quot;vBatDsp&quot;: 0.0,
                &quot;vBusP&quot;: 0.0,
                &quot;vBusN&quot;: 0.0,
                &quot;pf&quot;: 0.0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;deratingMode&quot;: 0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;realPower&quot;: 0,
                &quot;delayTime&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;batteryType&quot;: 0,
                &quot;vppWorkStatus&quot;: 0,
                &quot;pidStatus&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;vString9&quot;: 0.0,
                &quot;currentString9&quot;: 0.0,
                &quot;vString10&quot;: 0.0,
                &quot;currentString10&quot;: 0.0,
                &quot;vString11&quot;: 0.0,
                &quot;currentString11&quot;: 0.0,
                &quot;vString12&quot;: 0.0,
                &quot;currentString12&quot;: 0.0,
                &quot;vString13&quot;: 0.0,
                &quot;currentString13&quot;: 0.0,
                &quot;vString14&quot;: 0.0,
                &quot;currentString14&quot;: 0.0,
                &quot;vString15&quot;: 0.0,
                &quot;currentString15&quot;: 0.0,
                &quot;vString16&quot;: 0.0,
                &quot;currentString16&quot;: 0.0,
                &quot;strUnmatch&quot;: 0,
                &quot;strUnblance&quot;: 0,
                &quot;strBreak&quot;: 0,
                &quot;pidFaultCode&quot;: 0,
                &quot;stringPrompt&quot;: 0,
                &quot;warningValue1&quot;: 0,
                &quot;warningValue2&quot;: 0,
                &quot;faultValue&quot;: 0,
                &quot;flashEraseAgingOkFlag&quot;: 0,
                &quot;pvIso&quot;: 0,
                &quot;rDci&quot;: 0.0,
                &quot;sDci&quot;: 0.0,
                &quot;tDci&quot;: 0.0,
                &quot;pidBus&quot;: 0.0,
                &quot;gfci&quot;: 0,
                &quot;fanFaultBit&quot;: 0,
                &quot;sac&quot;: 0.0,
                &quot;reactPower&quot;: 0.0,
                &quot;reactPowerMax&quot;: 0.0,
                &quot;reactPowerTotal&quot;: 0.0,
                &quot;bAfciStatus&quot;: 0,
                &quot;vpv9&quot;: 0.0,
                &quot;vpv10&quot;: 0.0,
                &quot;ipv9&quot;: 0.0,
                &quot;ipv10&quot;: 0.0,
                &quot;ppv9&quot;: 0.0,
                &quot;ppv10&quot;: 0.0,
                &quot;epv9Today&quot;: 0.0,
                &quot;epv9Total&quot;: 0.0,
                &quot;epv10Today&quot;: 0.0,
                &quot;epv10Total&quot;: 0.0,
                &quot;vString17&quot;: 0.0,
                &quot;vString18&quot;: 0.0,
                &quot;vString19&quot;: 0.0,
                &quot;vString20&quot;: 0.0,
                &quot;currentString17&quot;: 0.0,
                &quot;currentString18&quot;: 0.0,
                &quot;currentString19&quot;: 0.0,
                &quot;currentString20&quot;: 0.0,
                &quot;strUnmatch2&quot;: 0,
                &quot;strUnblance2&quot;: 0,
                &quot;strBreak2&quot;: 0,
                &quot;warningValue3&quot;: 0,
                &quot;strWaringvalue1&quot;: 0,
                &quot;strWaringvalue2&quot;: 0,
                &quot;vbat&quot;: 0.0,
                &quot;cbat&quot;: 0.0,
                &quot;vac&quot;: 0.0,
                &quot;vacs&quot;: 0.0,
                &quot;vact&quot;: 0.0,
                &quot;vacRs&quot;: 0.0,
                &quot;vacSt&quot;: 0.0,
                &quot;vacTr&quot;: 0.0,
                &quot;iacLoad&quot;: 0.0,
                &quot;iacsLoad&quot;: 0.0,
                &quot;iactLoad&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;esystemtoday&quot;: 0.0,
                &quot;edischarge1Today&quot;: 0.0,
                &quot;edischarge1Total&quot;: 0.0,
                &quot;echarge1Today&quot;: 0.0,
                &quot;echarge1Total&quot;: 0.0,
                &quot;acChargeEnergyToday&quot;: 0.0,
                &quot;acChargeEnergyTotal&quot;: 0.0,
                &quot;esystemtotal&quot;: 0.0,
                &quot;eselftoday&quot;: 0.0,
                &quot;eselftotal&quot;: 0.0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 0.0,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;psystem&quot;: 0.0,
                &quot;busCapUsing&quot;: 0,
                &quot;runTime&quot;: 0,
                &quot;batPower&quot;: 0.0,
                &quot;soc&quot;: 0,
                &quot;soh&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;pex&quot;: 0.0,
                &quot;eexToday&quot;: 0.0,
                &quot;eexTotal&quot;: 0.0,
                &quot;udOpRSTWattSec&quot;: 0.0,
                &quot;uwFreqSec&quot;: 0.0,
                &quot;uwOpPhaseRVoltSec&quot;: 0.0,
                &quot;uwOpPhaseRCurrSec&quot;: 0.0,
                &quot;udOpRWattSec&quot;: 0.0,
                &quot;uwOpPhaseSVoltSec&quot;: 0.0,
                &quot;uwOpPhaseSCurrSec&quot;: 0.0,
                &quot;udOpSWattSec&quot;: 0.0,
                &quot;uwOpPhaseTVoltSec&quot;: 0.0,
                &quot;uwOpPhaseTCurrSec&quot;: 0.0,
                &quot;udOpTWattSec&quot;: 0.0,
                &quot;uwOpLineRSSec&quot;: 0.0,
                &quot;uwOpLineSTSec&quot;: 0.0,
                &quot;uwOpLineTRSec&quot;: 0.0,
                &quot;uwInvSec&quot;: 0.0,
                &quot;uwAmbientSec&quot;: 0.0,
                &quot;uwOutputSec&quot;: 0.0,
                &quot;uwPBusVoltSec&quot;: 0.0,
                &quot;uwNBusVoltSec&quot;: 0.0,
                &quot;uwMainCodeSec&quot;: 0,
                &quot;uwSubCodeSec&quot;: 0,
                &quot;uwMainWarnSec&quot;: 0,
                &quot;uwSubWarnSec&quot;: 0,
                &quot;udCalibApparentPowerSec&quot;: 0.0,
                &quot;reactivePowerRealValueSec&quot;: 0.0,
                &quot;bStatusSec&quot;: 0,
                &quot;invRVoltSec&quot;: 0.0,
                &quot;invSVoltSec&quot;: 0.0,
                &quot;invTVoltSec&quot;: 0.0,
                &quot;uwLoadPerSec&quot;: 0,
                &quot;onOffGridStateSec&quot;: 0,
                &quot;uwRDCICurrSec&quot;: 0.0,
                &quot;uwSDCICurrSec&quot;: 0.0,
                &quot;uwTDCICurrSec&quot;: 0.0,
                &quot;batVoltSec&quot;: 0.0,
                &quot;batCurrSec&quot;: 0.0,
                &quot;udOpRSTWattFirst&quot;: 0.0,
                &quot;uwFreqFirst&quot;: 0.0,
                &quot;uwOpPhaseRVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseRCurrFirst&quot;: 0.0,
                &quot;udOpRWattFirst&quot;: 0.0,
                &quot;uwOpPhaseSVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseSCurrFirst&quot;: 0.0,
                &quot;udOpSWattFirst&quot;: 0.0,
                &quot;uwOpPhaseTVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseTCurrFirst&quot;: 0.0,
                &quot;udOpTWattFirst&quot;: 0.0,
                &quot;uwOpLineRSFirst&quot;: 0.0,
                &quot;uwOpLineSTFirst&quot;: 0.0,
                &quot;uwOpLineTRFirst&quot;: 0.0,
                &quot;uwInvFirst&quot;: 0.0,
                &quot;uwAmbientFirst&quot;: 0.0,
                &quot;uwOutputFirst&quot;: 0.0,
                &quot;uwPBusVoltFirst&quot;: 0.0,
                &quot;uwNBusVoltFirst&quot;: 0.0,
                &quot;uwMainCodeFirst&quot;: 0,
                &quot;uwSubCodeFirst&quot;: 0,
                &quot;uwMainWarnFirst&quot;: 0,
                &quot;uwSubWarnFirst&quot;: 0,
                &quot;udCalibApparentPowerFirst&quot;: 0.0,
                &quot;reactivePowerRealValueFirst&quot;: 0.0,
                &quot;bStatusFirst&quot;: 0,
                &quot;invRVoltFirst&quot;: 0.0,
                &quot;invSVoltFirst&quot;: 0.0,
                &quot;invTVoltFirst&quot;: 0.0,
                &quot;uwLoadPerFirst&quot;: 0,
                &quot;onOffGridStateFirst&quot;: 0,
                &quot;uwRDCICurrFirst&quot;: 0.0,
                &quot;uwSDCICurrFirst&quot;: 0.0,
                &quot;uwTDCICurrFirst&quot;: 0.0,
                &quot;batVoltFirst&quot;: 0.0,
                &quot;batCurrFirst&quot;: 0.0,
                &quot;onOffGridState&quot;: 0,
                &quot;uBatChgP&quot;: 0.0,
                &quot;uBatDsgP&quot;: 0.0,
                &quot;uAcPower&quot;: 0.0,
                &quot;bClusterCnt&quot;: 0,
                &quot;bPacksCnt&quot;: 0,
                &quot;bSigPackModeCnt&quot;: 0,
                &quot;bSigModeCellCnt&quot;: 0,
                &quot;uwModeRatedVol&quot;: 0.0,
                &quot;uwModeRatedCap&quot;: 0.0,
                &quot;uwSysMaxAllowIchg&quot;: 0.0,
                &quot;uwSysMaxAllowIdis&quot;: 0.0,
                &quot;uwSysMaxVtotalchg&quot;: 0.0,
                &quot;uwSysMinVtotaldis&quot;: 0.0,
                &quot;uwCellMaxVChg&quot;: 0.0,
                &quot;uwCellMinVDis&quot;: 0.0,
                &quot;uwChargeMaxVol&quot;: 0.0,
                &quot;bBmsSta&quot;: 0,
                &quot;bFlagChgDis&quot;: 0,
                &quot;sysOnPackCnt&quot;: 0.0,
                &quot;bSoc&quot;: 0.0,
                &quot;bSoh&quot;: 0.0,
                &quot;uwRatedBatteryCapacity&quot;: 0.0,
                &quot;uwFullChargeCapacity&quot;: 0.0,
                &quot;uwUpackRated&quot;: 0.0,
                &quot;uwSysTotaVolValue&quot;: 0.0,
                &quot;uwSysLoadVolValue&quot;: 0.0,
                &quot;uwSysTotalIValue&quot;: 0.0,
                &quot;uwRatedBatteryPowerEnergy&quot;: 0.0,
                &quot;hcpcMaxVoltNum&quot;: 0.0,
                &quot;uwModMaxVolValue&quot;: 0.0,
                &quot;uwModeAvgVolValue&quot;: 0.0,
                &quot;hcpcLowVoltNum&quot;: 0.0,
                &quot;uwModeMinVolValue&quot;: 0.0,
                &quot;hcpcTempNum&quot;: 0.0,
                &quot;hcpcTempNum1&quot;: 0.0,
                &quot;uwModMinBlaTempValue&quot;: 0.0,
                &quot;uwModMaxBlaTempValue&quot;: 0.0,
                &quot;hcpcSingleMaxTempNum&quot;: 0.0,
                &quot;uwCellTmaxValue&quot;: 0.0,
                &quot;uwCellTavgValue&quot;: 0.0,
                &quot;hcpcSingleLowTempNum&quot;: 0.0,
                &quot;uwCellTminValue&quot;: 0.0,
                &quot;hcpcSingleMaxVoltNum&quot;: 0.0,
                &quot;uwCellUmaxValue&quot;: 0.0,
                &quot;uwCellUavgValue&quot;: 0.0,
                &quot;hcpcSingleLowVoltNum&quot;: 0.0,
                &quot;uwCellUminValue&quot;: 0.0,
                &quot;bSysMaxSocPackNum&quot;: 0.0,
                &quot;bSysMinSocPackNum&quot;: 0.0,
                &quot;bSysMaxSoc&quot;: 0,
                &quot;bSysMinSoc&quot;: 0,
                &quot;bSysAvgSoc&quot;: 0,
                &quot;udAccChgSoe&quot;: 0.0,
                &quot;uwFaultCode&quot;: 0,
                &quot;bFaultSubCode&quot;: 0,
                &quot;uwAlarmCode&quot;: 0,
                &quot;bAlarmSubCode&quot;: 0,
                &quot;udAccDisSoe&quot;: 0.0,
                &quot;soc2&quot;: 0.0,
                &quot;vbat2&quot;: 0.0,
                &quot;cbat2&quot;: 0.0,
                &quot;batPower2&quot;: 0.0,
                &quot;edischarge2Today&quot;: 0.0,
                &quot;edischarge2Total&quot;: 0.0,
                &quot;echarge2Today&quot;: 0.0,
                &quot;echarge2Total&quot;: 0.0,
                &quot;soc3&quot;: 0.0,
                &quot;vbat3&quot;: 0.0,
                &quot;cbat3&quot;: 0.0,
                &quot;batPower3&quot;: 0.0,
                &quot;edischarge3Today&quot;: 0.0,
                &quot;edischarge3Total&quot;: 0.0,
                &quot;echarge3Today&quot;: 0.0,
                &quot;echarge3Total&quot;: 0.0,
                &quot;genPort1Volt&quot;: 0.0,
                &quot;genPort2Volt&quot;: 0.0,
                &quot;genPort3Volt&quot;: 0.0,
                &quot;reverseCurr1&quot;: 0.0,
                &quot;reverseCurr2&quot;: 0.0,
                &quot;reverseCurr3&quot;: 0.0,
                &quot;batType&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;soh2&quot;: 0,
                &quot;soh3&quot;: 0,
                &quot;witBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;uwBatEnable1&quot;: 0,
                &quot;uwBatEnable2&quot;: 0,
                &quot;uwBatEnable3&quot;: 0,
                &quot;time&quot;: &quot;2024-05-29 14:54:18&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;statusText&quot;: &quot;Operating&quot;,
                &quot;again&quot;: false,
                &quot;usbagingTestOkFlag&quot;: 0
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
| :------------- | :--- | :---------- |
| serialNum | String | Serial Number |
| calendar | Calendar | Time |
| withTime | boolean | Whether the incoming data includes time |
| status | int | Min Status 0: waiting, 1: normal, 2: fault |
| isAgain | boolean | Whether it is a retransmission |
| ppv | double | Total PV input power |
| ppv1 | double | PV1 input power |
| ppv2 | double | PV2 input power |
| ppv3 | double | PV3 input power |
| pac | double | Inverter output power |
| pacToUserTotal | double | Total power to grid (forward) |
| pacToGridTotal | double | Total power to grid (reverse) |
| pacToLocalLoad | double | Total load power |
| timeTotal | double | Total runtime |
| epsPac | float | Off-grid output power |
| vpv1 | float | PV1 input voltage |
| ipv1 | float | PV1 input current |
| vpv2 | float | PV2 input voltage |
| ipv2 | float | PV2 input current |
| vpv3 | float | PV3 input voltage |
| ipv3 | float | PV3 input current |
| fac | float | Grid frequency |
| vac1 | float | Grid voltage 1 |
| iac1 | float | Grid current 1 |
| pac1 | float | Inverter apparent power 1 |
| vac2 | float | Grid voltage 2 |
| iac2 | float | Grid current 2 |
| pac2 | float | Inverter apparent power 2 |
| vac3 | float | Grid voltage 3 |
| iac3 | float | Grid current 3 |
| pac3 | float | Inverter apparent power 3 |
| vacRs | float | RS line voltage |
| vacSt | float | ST line voltage |
| vacTr | float | TR line voltage |
| eacToday | float | Inverter daily output energy |
| eacTotal | double | Inverter total output energy |
| epv1Today | float | PV1 daily generation |
| epv2Today | float | PV2 daily generation |
| epv3Today | float | PV3 daily generation |
| temp1 | float | Temperature 1 |
| temp2 | float | Temperature 2 |
| temp3 | float | Temperature 3 |
| temp4 | float | Temperature 4 |
| temp5 | float | Temperature 5 |
| pBusVoltage | float | P Bus voltage |
| nBusVoltage | float | N Bus voltage |
| opFullwatt | float | Output power limit |
| invDelayTime | float | Grid-tied inverter countdown |
| pf | float | Power factor value |
| epsPf | float | Off-grid power factor value |
| dcVoltage | float | DC voltage |
| epsFac | float | Off-grid frequency |
| epsVac1 | float | Off-grid R voltage |
| epsIac1 | float | Off-grid R current |
| epsPac1 | float | Off-grid R power |
| epsVac2 | float | Off-grid S voltage |
| epsIac2 | float | Off-grid S current |
| epsPac2 | float | Off-grid S power |
| epsVac3 | float | Off-grid T voltage |
| epsIac3 | float | Off-grid T current |
| epsPac3 | float | Off-grid T power |
| dciR | float | R-phase DC current component |
| dciS | float | S-phase DC current component |
| dciT | float | T-phase DC current component |
| sysFaultWord | int | 1001 |
| sysFaultWord1 | int | 1002 |
| sysFaultWord2 | int | 1003 |
| sysFaultWord3 | int | 1004 |
| sysFaultWord4 | int | 1005 |
| sysFaultWord5 | int | 1006 |
| sysFaultWord6 | int | 1007 |
| sysFaultWord7 | int | 1008 |
| faultType | int | Fault code |
| warnCode | int | Warning code |
| realOPPercent | int | Real output percentage |
| deratingMode | int | Derating mode |
| bdcStatus | int | BDC connection status |
| dryContactStatus | int | Dry contact connection status |
| loadPercent | int | Off-grid load percentage |
| uwSysWorkMode | int | System work mode 1000 |
| gfci | int | Grid leakage current |
| iso | int | PV insulation resistance |
| etoUserToday | double | Grid daily output energy |
| etoUserTotal | double | Grid total output energy |
| etoGridToday | double | Grid daily input energy |
| etoGridTotal | double | Grid total input energy |
| elocalLoadToday | double | Daily energy consumption of user load |
| elocalLoadTotal | double | Total energy consumption of user load |
| epv1Total | double | PV1 total generation |
| epv2Total | double | PV2 total generation |
| epv3Total | double | PV3 total generation |
| epvTotal | double | Total PV generation |
| echargeToday | double | System daily charging energy |
| echargeTotal | double | System total charging energy |
| edischargeToday | double | System daily discharging energy |
| edischargeTotal | double | System total discharging energy |
| eacChargeToday | double | AC daily charging energy |
| eacChargeTotal | double | AC total charging energy |
| BDC Parameters | | |
| bdc1Status | int | BDC1 status |
| bdc1Mode | int | BDC1 mode |
| bdc1FaultType | int | BDC1 fault code |
| bdc1WarnCode | int | BDC1 warning code |
| bdc1Vbat | float | BDC1 battery voltage |
| bdc1Ibat | float | BDC1 battery current |
| bdc1Soc | int | BDC1 battery capacity |
| bdc1Vbus1 | float | BDC1 Bus1 voltage |
| bdc1Vbus2 | float | BDC1 Bus2 voltage |
| bdc1Ibb | float | BDC1 BUCK-BOOST current |
| bdc1Illc | float | BDC1 LLC current |
| bdc1Temp1 | float | BDC1 Temperature A |
| bdc1Temp2 | float | BDC1 Temperature B |
| bdc1DischargePower | double | BDC1 discharge power |
| bdc1ChargePower | double | BDC1 charge power |
| bdc1DischargeTotal | double | BDC1 total discharge energy |
| bdc1ChargeTotal | double | BDC1 total charge energy |
| bdc2Status | int | BDC2 status |
| bdc2Mode | int | BDC2 mode |
| bdc2FaultType | int | BDC2 fault code |
| bdc2WarnCode | int | BDC2 warning code |
| bdc2Vbat | float | BDC2 battery voltage |
| bdc2Ibat | float | BDC2 battery current |
| bdc2Soc | int | BDC2 battery capacity |
| bdc2Vbus1 | float | BDC2 Bus1 voltage |
| bdc2Vbus2 | float | BDC2 Bus2 voltage |
| bdc2Ibb | float | BDC2 BUCK-BOOST current |
| bdc2Illc | float | BDC2 LLC current |
| bdc2Temp1 | float | BDC2 Temperature A |
| bdc2Temp2 | float | BDC2 Temperature B |
| bdc2DischargePower | double | BDC2 discharge power |
| bdc2ChargePower | double | BDC2 charge power |
| bdc2DischargeTotal | double | BDC2 total discharge energy |
| bdc2ChargeTotal | double | BDC2 total charge energy |
| BMS Parameters | | |
| bmsStatus | int | BMS status |
| bmsFaultType | int | BMS fault code |
| bmsWarnCode | int | BMS warning code |
| bmsVbat | float | BMS battery voltage |
| bmsIbat | float | BMS battery current |
| bmsSoc | int | BMS battery capacity |
| bmsTemp1Bat | float | BMS battery temperature |
| bmsMaxCurr | float | BMS maximum current |
| bmsVdelta | float | BMS Delta voltage |
| bmsIcycle | int | BMS battery cycle count |
| bmsSoh | int | BMS battery health index |
| bmsCvVolt | float | BMS lithium battery CV voltage |
| bmsInfo | float | BMS information |
| bmsPackInfo | float | BMS pack information |
| bmsUsingCap | float | BMS battery capacity used |
| bmsFwVersion | String | BMS internal version |
| bmsMcuVersion | String | BMS battery MCU version |
| bmsCommunicationType | int | BMS communication type 0-RS485, 1-CAN |

**Notes**
- Data is fetched once within every 5 minutes.


---

# 33. wit device historical data

*Page ID: `11292928841081078`*

  
**Brief Description:**

- Data format and parameter description of wit device historical data
- `Only applicable to: obtaining all detailed data of a specific device for a certain day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-28&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;0ZFN00R23ZBF0002&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;calendar&quot;: 1716963248000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 1,
                &quot;ppv&quot;: 0.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;ppv4&quot;: 0.0,
                &quot;ppv5&quot;: 0.0,
                &quot;ppv6&quot;: 0.0,
                &quot;ppv7&quot;: 0.0,
                &quot;ppv8&quot;: 0.0,
                &quot;vpv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;vpv4&quot;: 0.0,
                &quot;vpv5&quot;: 0.0,
                &quot;vpv6&quot;: 0.0,
                &quot;vpv7&quot;: 0.0,
                &quot;vpv8&quot;: 0.0,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;ipv4&quot;: 0.0,
                &quot;ipv5&quot;: 0.0,
                &quot;ipv6&quot;: 0.0,
                &quot;ipv7&quot;: 0.0,
                &quot;ipv8&quot;: 0.0,
                &quot;pac&quot;: 0.0,
                &quot;fac&quot;: 0.0,
                &quot;vac1&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;pac1&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;vac3&quot;: 0.0,
                &quot;iac3&quot;: 0.0,
                &quot;pac3&quot;: 0.0,
                &quot;eacToday&quot;: 70.9,
                &quot;eacTotal&quot;: 5988.1,
                &quot;timeTotal&quot;: 1949155.0,
                &quot;epv1Today&quot;: 0.0,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 0.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epv4Today&quot;: 0.0,
                &quot;epv4Total&quot;: 0.0,
                &quot;epv5Today&quot;: 0.0,
                &quot;epv5Total&quot;: 0.0,
                &quot;epv6Today&quot;: 0.0,
                &quot;epv6Total&quot;: 0.0,
                &quot;epv7Today&quot;: 0.0,
                &quot;epv7Total&quot;: 0.0,
                &quot;epv8Today&quot;: 0.0,
                &quot;epv8Total&quot;: 0.0,
                &quot;epvToday&quot;: 0.0,
                &quot;epvTotal&quot;: 0.0,
                &quot;temp1&quot;: 0.0,
                &quot;temp2&quot;: 0.0,
                &quot;temp3&quot;: 0.0,
                &quot;vBatDsp&quot;: 0.0,
                &quot;vBusP&quot;: 0.0,
                &quot;vBusN&quot;: 0.0,
                &quot;pf&quot;: 0.0,
                &quot;realOPPercent&quot;: 0,
                &quot;opFullwatt&quot;: 0.0,
                &quot;deratingMode&quot;: 0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;realPower&quot;: 0,
                &quot;delayTime&quot;: 0,
                &quot;errorCode&quot;: 0,
                &quot;priorityChoose&quot;: 1,
                &quot;batteryType&quot;: 0,
                &quot;vppWorkStatus&quot;: 0,
                &quot;pidStatus&quot;: 0,
                &quot;vString1&quot;: 0.0,
                &quot;currentString1&quot;: 0.0,
                &quot;vString2&quot;: 0.0,
                &quot;currentString2&quot;: 0.0,
                &quot;vString3&quot;: 0.0,
                &quot;currentString3&quot;: 0.0,
                &quot;vString4&quot;: 0.0,
                &quot;currentString4&quot;: 0.0,
                &quot;vString5&quot;: 0.0,
                &quot;currentString5&quot;: 0.0,
                &quot;vString6&quot;: 0.0,
                &quot;currentString6&quot;: 0.0,
                &quot;vString7&quot;: 0.0,
                &quot;currentString7&quot;: 0.0,
                &quot;vString8&quot;: 0.0,
                &quot;currentString8&quot;: 0.0,
                &quot;vString9&quot;: 0.0,
                &quot;currentString9&quot;: 0.0,
                &quot;vString10&quot;: 0.0,
                &quot;currentString10&quot;: 0.0,
                &quot;vString11&quot;: 0.0,
                &quot;currentString11&quot;: 0.0,
                &quot;vString12&quot;: 0.0,
                &quot;currentString12&quot;: 0.0,
                &quot;vString13&quot;: 0.0,
                &quot;currentString13&quot;: 0.0,
                &quot;vString14&quot;: 0.0,
                &quot;currentString14&quot;: 0.0,
                &quot;vString15&quot;: 0.0,
                &quot;currentString15&quot;: 0.0,
                &quot;vString16&quot;: 0.0,
                &quot;currentString16&quot;: 0.0,
                &quot;strUnmatch&quot;: 0,
                &quot;strUnblance&quot;: 0,
                &quot;strBreak&quot;: 0,
                &quot;pidFaultCode&quot;: 0,
                &quot;stringPrompt&quot;: 0,
                &quot;warningValue1&quot;: 0,
                &quot;warningValue2&quot;: 0,
                &quot;faultValue&quot;: 0,
                &quot;flashEraseAgingOkFlag&quot;: 0,
                &quot;pvIso&quot;: 0,
                &quot;rDci&quot;: 0.0,
                &quot;sDci&quot;: 0.0,
                &quot;tDci&quot;: 0.0,
                &quot;pidBus&quot;: 0.0,
                &quot;gfci&quot;: 0,
                &quot;fanFaultBit&quot;: 0,
                &quot;sac&quot;: 0.0,
                &quot;reactPower&quot;: 0.0,
                &quot;reactPowerMax&quot;: 0.0,
                &quot;reactPowerTotal&quot;: 0.0,
                &quot;bAfciStatus&quot;: 0,
                &quot;vpv9&quot;: 0.0,
                &quot;vpv10&quot;: 0.0,
                &quot;ipv9&quot;: 0.0,
                &quot;ipv10&quot;: 0.0,
                &quot;ppv9&quot;: 0.0,
                &quot;ppv10&quot;: 0.0,
                &quot;epv9Today&quot;: 0.0,
                &quot;epv9Total&quot;: 0.0,
                &quot;epv10Today&quot;: 0.0,
                &quot;epv10Total&quot;: 0.0,
                &quot;vString17&quot;: 0.0,
                &quot;vString18&quot;: 0.0,
                &quot;vString19&quot;: 0.0,
                &quot;vString20&quot;: 0.0,
                &quot;currentString17&quot;: 0.0,
                &quot;currentString18&quot;: 0.0,
                &quot;currentString19&quot;: 0.0,
                &quot;currentString20&quot;: 0.0,
                &quot;strUnmatch2&quot;: 0,
                &quot;strUnblance2&quot;: 0,
                &quot;strBreak2&quot;: 0,
                &quot;warningValue3&quot;: 0,
                &quot;strWaringvalue1&quot;: 0,
                &quot;strWaringvalue2&quot;: 0,
                &quot;vbat&quot;: 777.0,
                &quot;cbat&quot;: 0.0,
                &quot;vac&quot;: 0.0,
                &quot;vacs&quot;: 0.0,
                &quot;vact&quot;: 0.0,
                &quot;vacRs&quot;: 0.0,
                &quot;vacSt&quot;: 0.0,
                &quot;vacTr&quot;: 0.0,
                &quot;iacLoad&quot;: 0.0,
                &quot;iacsLoad&quot;: 0.0,
                &quot;iactLoad&quot;: 0.0,
                &quot;pself&quot;: 0.0,
                &quot;esystemtoday&quot;: 72.80000305175781,
                &quot;edischarge1Today&quot;: 72.8,
                &quot;edischarge1Total&quot;: 6141.7,
                &quot;echarge1Today&quot;: 238.7,
                &quot;echarge1Total&quot;: 6468.9,
                &quot;acChargeEnergyToday&quot;: 242.5,
                &quot;acChargeEnergyTotal&quot;: 6576.60009765625,
                &quot;esystemtotal&quot;: 6141.7001953125,
                &quot;eselftoday&quot;: 0.0,
                &quot;eselftotal&quot;: 0.0,
                &quot;etoUserToday&quot;: 238.7,
                &quot;etoUserTotal&quot;: 6468.9,
                &quot;etoGridToday&quot;: 72.8,
                &quot;etoGridTotal&quot;: 6141.7,
                &quot;elocalLoadToday&quot;: 0.0,
                &quot;elocalLoadTotal&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;psystem&quot;: 0.0,
                &quot;busCapUsing&quot;: 0,
                &quot;runTime&quot;: 0,
                &quot;batPower&quot;: 0.0,
                &quot;soc&quot;: 100,
                &quot;soh&quot;: 100,
                &quot;bmsBatteryVolt&quot;: 777.0,
                &quot;pex&quot;: 0.0,
                &quot;eexToday&quot;: 0.0,
                &quot;eexTotal&quot;: 0.0,
                &quot;udOpRSTWattSec&quot;: 0.0,
                &quot;uwFreqSec&quot;: 0.0,
                &quot;uwOpPhaseRVoltSec&quot;: 0.0,
                &quot;uwOpPhaseRCurrSec&quot;: 0.0,
                &quot;udOpRWattSec&quot;: 0.0,
                &quot;uwOpPhaseSVoltSec&quot;: 0.0,
                &quot;uwOpPhaseSCurrSec&quot;: 0.0,
                &quot;udOpSWattSec&quot;: 0.0,
                &quot;uwOpPhaseTVoltSec&quot;: 0.0,
                &quot;uwOpPhaseTCurrSec&quot;: 0.0,
                &quot;udOpTWattSec&quot;: 0.0,
                &quot;uwOpLineRSSec&quot;: 0.0,
                &quot;uwOpLineSTSec&quot;: 0.0,
                &quot;uwOpLineTRSec&quot;: 0.0,
                &quot;uwInvSec&quot;: 0.0,
                &quot;uwAmbientSec&quot;: 0.0,
                &quot;uwOutputSec&quot;: 0.0,
                &quot;uwPBusVoltSec&quot;: 0.0,
                &quot;uwNBusVoltSec&quot;: 0.0,
                &quot;uwMainCodeSec&quot;: 0,
                &quot;uwSubCodeSec&quot;: 0,
                &quot;uwMainWarnSec&quot;: 0,
                &quot;uwSubWarnSec&quot;: 0,
                &quot;udCalibApparentPowerSec&quot;: 0.0,
                &quot;reactivePowerRealValueSec&quot;: 0.0,
                &quot;bStatusSec&quot;: 0,
                &quot;invRVoltSec&quot;: 0.0,
                &quot;invSVoltSec&quot;: 0.0,
                &quot;invTVoltSec&quot;: 0.0,
                &quot;uwLoadPerSec&quot;: 0,
                &quot;onOffGridStateSec&quot;: 0,
                &quot;uwRDCICurrSec&quot;: 0.0,
                &quot;uwSDCICurrSec&quot;: 0.0,
                &quot;uwTDCICurrSec&quot;: 0.0,
                &quot;batVoltSec&quot;: 0.0,
                &quot;batCurrSec&quot;: 0.0,
                &quot;udOpRSTWattFirst&quot;: 0.0,
                &quot;uwFreqFirst&quot;: 0.0,
                &quot;uwOpPhaseRVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseRCurrFirst&quot;: 0.0,
                &quot;udOpRWattFirst&quot;: 0.0,
                &quot;uwOpPhaseSVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseSCurrFirst&quot;: 0.0,
                &quot;udOpSWattFirst&quot;: 0.0,
                &quot;uwOpPhaseTVoltFirst&quot;: 0.0,
                &quot;uwOpPhaseTCurrFirst&quot;: 0.0,
                &quot;udOpTWattFirst&quot;: 0.0,
                &quot;uwOpLineRSFirst&quot;: 0.0,
                &quot;uwOpLineSTFirst&quot;: 0.0,
                &quot;uwOpLineTRFirst&quot;: 0.0,
                &quot;uwInvFirst&quot;: 0.0,
                &quot;uwAmbientFirst&quot;: 0.0,
                &quot;uwOutputFirst&quot;: 0.0,
                &quot;uwPBusVoltFirst&quot;: 0.0,
                &quot;uwNBusVoltFirst&quot;: 0.0,
                &quot;uwMainCodeFirst&quot;: 0,
                &quot;uwSubCodeFirst&quot;: 0,
                &quot;uwMainWarnFirst&quot;: 0,
                &quot;uwSubWarnFirst&quot;: 0,
                &quot;udCalibApparentPowerFirst&quot;: 0.0,
                &quot;reactivePowerRealValueFirst&quot;: 0.0,
                &quot;bStatusFirst&quot;: 0,
                &quot;invRVoltFirst&quot;: 0.0,
                &quot;invSVoltFirst&quot;: 0.0,
                &quot;invTVoltFirst&quot;: 0.0,
                &quot;uwLoadPerFirst&quot;: 0,
                &quot;onOffGridStateFirst&quot;: 0,
                &quot;uwRDCICurrFirst&quot;: 0.0,
                &quot;uwSDCICurrFirst&quot;: 0.0,
                &quot;uwTDCICurrFirst&quot;: 0.0,
                &quot;batVoltFirst&quot;: 0.0,
                &quot;batCurrFirst&quot;: 0.0,
                &quot;onOffGridState&quot;: 0,
                &quot;uBatChgP&quot;: 0.0,
                &quot;uBatDsgP&quot;: 0.0,
                &quot;uAcPower&quot;: 0.0,
                &quot;bClusterCnt&quot;: 0,
                &quot;bPacksCnt&quot;: 0,
                &quot;bSigPackModeCnt&quot;: 0,
                &quot;bSigModeCellCnt&quot;: 0,
                &quot;uwModeRatedVol&quot;: 0.0,
                &quot;uwModeRatedCap&quot;: 0.0,
                &quot;uwSysMaxAllowIchg&quot;: 0.0,
                &quot;uwSysMaxAllowIdis&quot;: 0.0,
                &quot;uwSysMaxVtotalchg&quot;: 0.0,
                &quot;uwSysMinVtotaldis&quot;: 0.0,
                &quot;uwCellMaxVChg&quot;: 0.0,
                &quot;uwCellMinVDis&quot;: 0.0,
                &quot;uwChargeMaxVol&quot;: 0.0,
                &quot;bBmsSta&quot;: 1,
                &quot;bFlagChgDis&quot;: 0,
                &quot;sysOnPackCnt&quot;: 0.0,
                &quot;bSoc&quot;: 100.0,
                &quot;bSoh&quot;: 100.0,
                &quot;uwRatedBatteryCapacity&quot;: 0.0,
                &quot;uwFullChargeCapacity&quot;: 0.0,
                &quot;uwUpackRated&quot;: 0.0,
                &quot;uwSysTotaVolValue&quot;: 0.0,
                &quot;uwSysLoadVolValue&quot;: 779.9,
                &quot;uwSysTotalIValue&quot;: -0.2,
                &quot;uwRatedBatteryPowerEnergy&quot;: 0.0,
                &quot;hcpcMaxVoltNum&quot;: 0.0,
                &quot;uwModMaxVolValue&quot;: 0.0,
                &quot;uwModeAvgVolValue&quot;: 0.0,
                &quot;hcpcLowVoltNum&quot;: 0.0,
                &quot;uwModeMinVolValue&quot;: 0.0,
                &quot;hcpcTempNum&quot;: 0.0,
                &quot;hcpcTempNum1&quot;: 0.0,
                &quot;uwModMinBlaTempValue&quot;: 0.0,
                &quot;uwModMaxBlaTempValue&quot;: 0.0,
                &quot;hcpcSingleMaxTempNum&quot;: 0.0,
                &quot;uwCellTmaxValue&quot;: 0.0,
                &quot;uwCellTavgValue&quot;: 0.0,
                &quot;hcpcSingleLowTempNum&quot;: 0.0,
                &quot;uwCellTminValue&quot;: 0.0,
                &quot;hcpcSingleMaxVoltNum&quot;: 0.0,
                &quot;uwCellUmaxValue&quot;: 0.0,
                &quot;uwCellUavgValue&quot;: 0.0,
                &quot;hcpcSingleLowVoltNum&quot;: 0.0,
                &quot;uwCellUminValue&quot;: 0.0,
                &quot;bSysMaxSocPackNum&quot;: 0.0,
                &quot;bSysMinSocPackNum&quot;: 0.0,
                &quot;bSysMaxSoc&quot;: 0,
                &quot;bSysMinSoc&quot;: 0,
                &quot;bSysAvgSoc&quot;: 100,
                &quot;udAccChgSoe&quot;: 6625.5,
                &quot;uwFaultCode&quot;: 0,
                &quot;bFaultSubCode&quot;: 0,
                &quot;uwAlarmCode&quot;: 0,
                &quot;bAlarmSubCode&quot;: 0,
                &quot;udAccDisSoe&quot;: 6125.0,
                &quot;soc2&quot;: 0.0,
                &quot;vbat2&quot;: 0.0,
                &quot;cbat2&quot;: 0.0,
                &quot;batPower2&quot;: 0.0,
                &quot;edischarge2Today&quot;: 0.0,
                &quot;edischarge2Total&quot;: 0.0,
                &quot;echarge2Today&quot;: 0.0,
                &quot;echarge2Total&quot;: 0.0,
                &quot;soc3&quot;: 0.0,
                &quot;vbat3&quot;: 0.0,
                &quot;cbat3&quot;: 0.0,
                &quot;batPower3&quot;: 0.0,
                &quot;edischarge3Today&quot;: 0.0,
                &quot;edischarge3Total&quot;: 0.0,
                &quot;echarge3Today&quot;: 0.0,
                &quot;echarge3Total&quot;: 0.0,
                &quot;genPort1Volt&quot;: 0.0,
                &quot;genPort2Volt&quot;: 0.0,
                &quot;genPort3Volt&quot;: 0.0,
                &quot;reverseCurr1&quot;: 0.0,
                &quot;reverseCurr2&quot;: 0.0,
                &quot;reverseCurr3&quot;: 0.0,
                &quot;batType&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;soh2&quot;: 0,
                &quot;soh3&quot;: 0,
                &quot;witBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;uwBatEnable1&quot;: 0,
                &quot;uwBatEnable2&quot;: 0,
                &quot;uwBatEnable3&quot;: 0,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Operating&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;usbagingTestOkFlag&quot;: 0,
                &quot;time&quot;: &quot;2024-05-29 14:14:08&quot;
            },
        ],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description**

| Parameter Name       | Type    | Description                                      |
|:---------------------|:--------|:------------------------------------------------- |
| serialNum            | String  | Serial Number                                    |
| calendar             | Calendar| Time                                             |
| withTime             | boolean | Indicates if the incoming data includes time     |
| status               | int     | Tlx Status: 0: waiting, 1: normal, 2: fault      |
| isAgain              | boolean | Indicates if it is a retransmission              |
| ppv                  | double  | Total PV input power                             |
| ppv1                 | double  | PV1 input power                                  |
| ppv2                 | double  | PV2 input power                                  |
| ppv3                 | double  | PV3 input power                                  |
| pac                  | double  | Inverter output power                            |
| pacToUserTotal       | double  | Total power flowing to the grid                  |
| pacToGridTotal       | double  | Total power flowing back to the grid             |
| pacToLocalLoad       | double  | Total load power                                 |
| timeTotal            | double  | Total runtime                                    |
| epsPac               | float   | Off-grid output power                            |
| vpv1                 | float   | PV1 input voltage                                |
| ipv1                 | float   | PV1 input current                                |
| vpv2                 | float   | PV2 input voltage                                |
| ipv2                 | float   | PV2 input current                                |
| vpv3                 | float   | PV3 input voltage                                |
| ipv3                 | float   | PV3 input current                                |
| fac                  | float   | Grid frequency                                   |
| vac1                 | float   | Grid voltage 1                                   |
| iac1                 | float   | Grid current 1                                   |
| pac1                 | float   | Inverter apparent power output 1                 |
| vac2                 | float   | Grid voltage 2                                   |
| iac2                 | float   | Grid current 2                                   |
| pac2                 | float   | Inverter apparent power output 2                 |
| vac3                 | float   | Grid voltage 3                                   |
| iac3                 | float   | Grid current 3                                   |
| pac3                 | float   | Inverter apparent power output 3                 |
| vacRs                | float   | RS line voltage                                  |
| vacSt                | float   | ST line voltage                                  |
| vacTr                | float   | TR line voltage                                  |
| eacToday             | float   | Inverter daily output energy                     |
| eacTotal             | double  | Inverter total output energy                     |
| epv1Today            | float   | PV1 daily energy generation                      |
| epv2Today            | float   | PV2 daily energy generation                      |
| epv3Today            | float   | PV3 daily energy generation                      |
| temp1                | float   | Temperature 1                                    |
| temp2                | float   | Temperature 2                                    |
| temp3                | float   | Temperature 3                                    |
| temp4                | float   | Temperature 4                                    |
| temp5                | float   | Temperature 5                                    |
| pBusVoltage          | float   | P Bus voltage                                    |
| nBusVoltage          | float   | N Bus voltage                                    |
| opFullwatt           | float   | Output power limit                               |
| invDelayTime         | float   | Grid-tied inverter countdown                     |
| pf                   | float   | Power factor (pf) value                          |
| epsPf                | float   | Off-grid power factor (pf) value                 |
| dcVoltage            | float   | DC voltage                                       |
| epsFac               | float   | Off-grid frequency                               |
| epsVac1              | float   | Off-grid R voltage                               |
| epsIac1              | float   | Off-grid R current                               |
| epsPac1              | float   | Off-grid R power                                 |
| epsVac2              | float   | Off-grid S voltage                               |
| epsIac2              | float   | Off-grid S current                               |
| epsPac2              | float   | Off-grid S power                                 |
| epsVac3              | float   | Off-grid T voltage                               |
| epsIac3              | float   | Off-grid T current                               |
| epsPac3              | float   | Off-grid T power                                 |
| dciR                 | float   | R phase DC current component                     |
| dciS                 | float   | S phase DC current component                     |
| dciT                 | float   | T phase DC current component                     |
| sysFaultWord         | int     | System fault word 1001                           |
| sysFaultWord1        | int     | System fault word 1002                           |
| sysFaultWord2        | int     | System fault word 1003                           |
| sysFaultWord3        | int     | System fault word 1004                           |
| sysFaultWord4        | int     | System fault word 1005                           |
| sysFaultWord5        | int     | System fault word 1006                           |
| sysFaultWord6        | int     | System fault word 1007                           |
| sysFaultWord7        | int     | System fault word 1008                           |
| faultType            | int     | Fault code                                       |
| warnCode             | int     | Warning code                                     |
| realOPPercent        | int     | R                                                |
| deratingMode         | int     | Derating mode                                    |
| bdcStatus            | int     | BDC connection status                            |
| dryContactStatus     | int     | Dry contact connection status                    |
| loadPercent          | int     | Off-grid load percentage                         |
| uwSysWorkMode        | int     | System working mode 1000                         |
| gfci                 | int     | Grid leakage current                             |
| iso                  | int     | PV insulation resistance                         |
| etoUserToday         | double  | Grid daily export energy                         |
| etoUserTotal         | double  | Grid total export energy                         |
| etoGridToday         | double  | Grid daily import energy                         |
| etoGridTotal         | double  | Grid total import energy                         |
| elocalLoadToday      | double  | User load daily energy consumption               |
| elocalLoadTotal      | double  | User load total energy consumption               |
| epv1Total            | double  | PV1 total energy generation                      |
| epv2Total            | double  | PV2 total energy generation                      |
| epv3Total            | double  | PV3 total energy generation                      |
| epvTotal             | double  | Total PV energy generation                       |
| echargeToday         | double  | System daily charging energy                     |
| echargeTotal         | double  | System total charging energy                     |
| edischargeToday      | double  | System daily discharging energy                  |
| edischargeTotal      | double  | System total discharging energy                  |
| eacChargeToday       | double  | AC daily charging energy                         |
| eacChargeTotal       | double  | AC total charging energy                         |
| BDC Parameters       |         |                                                  |
| bdc1Status           | int     | BDC1 status                                      |
| bdc1Mode             | int     | BDC1 mode                                        |
| bdc1FaultType        | int     | BDC1 fault code                                  |
| bdc1WarnCode         | int     | BDC1 warning code                                |
| bdc1Vbat             | float   | BDC1 battery voltage                             |
| bdc1Ibat             | float   | BDC1 battery current                             |
| bdc1Soc              | int     | BDC1 battery capacity                            |
| bdc1Vbus1            | float   | BDC1 Bus1 voltage                                |
| bdc1Vbus2            | float   | BDC1 Bus2 voltage                                |
| bdc1Ibb              | float   | BDC1 BUCK-BOOST Current                          |
| bdc1Illc             | float   | BDC1 LLC Current                                 |
| bdc1Temp1            | float   | BDC1 Temperature A                               |
| bdc1Temp2            | float   | BDC1 Temperature B                               |
| bdc1DischargePower   | double  | BDC1 discharge power                             |
| bdc1ChargePower      | double  | BDC1 charge power                                |
| bdc1DischargeTotal   | double  | BDC1 total discharge energy                      |
| bdc1ChargeTotal      | double  | BDC1 total charge energy                         |
| bdc2Status           | int     | BDC2 status                                      |
| bdc2Mode             | int     | BDC2 mode                                        |
| bdc2FaultType        | int     | BDC2 fault code                                  |
| bdc2WarnCode         | int     | BDC2 warning code                                |
| bdc2Vbat             | float   | BDC2 battery voltage                             |
| bdc2Ibat             | float   | BDC2 battery current                             |
| bdc2Soc              | int     | BDC2 battery capacity                            |
| bdc2Vbus1            | float   | BDC2 Bus1 voltage                                |
| bdc2Vbus2            | float   | BDC2 Bus2 voltage                                |
| bdc2Ibb              | float   | BDC2 BUCK-BOOST Current                          |
| bdc2Illc             | float   | BDC2 LLC Current                                 |
| bdc2Temp1            | float   | BDC2 Temperature A                               |
| bdc2Temp2            | float   | BDC2 Temperature B                               |
| bdc2DischargePower   | double  | BDC2 discharge power                             |
| bdc2ChargePower      | double  | BDC2 charge power                                |
| bdc2DischargeTotal   | double  | BDC2 total discharge energy                      |
| bdc2ChargeTotal      | double  | BDC2 total charge energy                         |
| BMS Parameters       |         |                                                  |
| bmsStatus            | int     | BMS status                                       |
| bmsFaultType         | int     | BMS fault code                                   |
| bmsWarnCode          | int     | BMS warning code                                 |
| bmsVbat              | float   | BDC2 battery voltage                             |
| bmsIbat              | float   | BDC2 battery current                             |
| bmsSoc               | int     | BDC2 battery capacity                            |
| bmsTemp1Bat          | float   | BDC2 battery temperature                         |
| bmsMaxCurr           | float   | BDC2 maximum current                             |
| bmsVdelta            | float   | BMS Delta voltage                                |
| bmsIcycle            | int     | BMS battery cycle count                          |
| bmsSoh               | int     | BMS battery health index                         |
| bmsCvVolt            | float   | BMS lithium battery CV voltage                   |
| bmsInfo              | float   | BMS information                                  |
| bmsPackInfo          | float   | BMS battery pack information                     |
| bmsUsingCap          | float   | BMS battery capacity                             |
| bmsFwVersion         | String  | BMS internal version                             |
| bmsMcuVersion        | String  | BMS battery MCU version                          |
| bmsCommunicationType | int     | BMS communication type: 0-RS485, 1-CAN           |

**Remarks**
- The retrieval frequency is once every 5 minutes

---

# 34. Basic Information of sph-s

*Page ID: `11292929153206911`*

  
**Brief Description:**

- Data return format of basic information for sph-s devices and explanation of some basic parameters
- `Only applicable to: batch retrieval of basic device information.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;sph-s&quot;: [
            {
                &quot;serialNum&quot;: &quot;AGP0N1600D&quot;,
                &quot;portName&quot;: &quot;ShinePano - VC51010323468084&quot;,
                &quot;dataLogSn&quot;: &quot;VC51010323468084&quot;,
                &quot;groupId&quot;: -1,
                &quot;alias&quot;: &quot;AGP0N1600D&quot;,
                &quot;location&quot;: &quot;&quot;,
                &quot;lost&quot;: false,
                &quot;status&quot;: 3,
                &quot;addr&quot;: 1,
                &quot;fwVersion&quot;: &quot;UL2.0&quot;,
                &quot;model&quot;: 0,
                &quot;tcpServerIp&quot;: &quot;47.119.16.193&quot;,
                &quot;version&quot;: &quot;ULSP0000xx&quot;,
                &quot;lastUpdateTime&quot;: 1716963973000,
                &quot;sysTime&quot;: &quot;2018-01-01 00:00:00&quot;,
                &quot;deviceType&quot;: 280,
                &quot;communicationVersion&quot;: &quot;SKaa-0001&quot;,
                &quot;power&quot;: 0.0,
                &quot;eToday&quot;: 0.0,
                &quot;eTotal&quot;: 0.0,
                &quot;powerMax&quot;: null,
                &quot;powerMaxTime&quot;: null,
                &quot;energyDay&quot;: 0.0,
                &quot;energyMonth&quot;: 0.0,
                &quot;energyDayMap&quot;: {},
                &quot;pmax&quot;: 15000,
                &quot;vnormal&quot;: 350.0,
                &quot;lcdLanguage&quot;: 1,
                &quot;countrySelected&quot;: 1,
                &quot;wselectBaudrate&quot;: 0,
                &quot;comAddress&quot;: 1,
                &quot;manufacturer&quot;: &quot;www.sacolar.com&quot;,
                &quot;failsafe&quot;: 0,
                &quot;dtc&quot;: 21200,
                &quot;modbusVersion&quot;: 207,
                &quot;voltageHighLimit&quot;: 264.0,
                &quot;voltageLowLimit&quot;: 213.0,
                &quot;freqHighLimit&quot;: 60.5,
                &quot;freqLowLimit&quot;: 59.3,
                &quot;pvPfCmdMemoryState&quot;: 0,
                &quot;activeRate&quot;: 100,
                &quot;reactiveRate&quot;: 100,
                &quot;exportLimit&quot;: 1,
                &quot;exportLimitPowerRate&quot;: 100.0,
                &quot;reactiveValue&quot;: 1000.0,
                &quot;reactiveOutputPriority&quot;: 1,
                &quot;uwNominalGridVolt&quot;: 0.0,
                &quot;uwReconnectStartSlope&quot;: 10.0,
                &quot;uwGridWattDelay&quot;: 1000,
                &quot;updating&quot;: false,
                &quot;record&quot;: null,
                &quot;userName&quot;: null,
                &quot;modelText&quot;: &quot;S00B00D00T00P00U00M0000&quot;,
                &quot;plantId&quot;: 0,
                &quot;plantName&quot;: null,
                &quot;timezone&quot;: 8.0,
                &quot;pCharge&quot;: 0.0,
                &quot;pDischarge&quot;: 0.0,
                &quot;sysTimeText&quot;: &quot;2018-01-01 00:00:00&quot;,
                &quot;sphSetBean&quot;: null,
                &quot;powerMaxText&quot;: &quot;&quot;,
                &quot;energyMonthText&quot;: &quot;0&quot;,
                &quot;treeName&quot;: &quot;AGP0N1600D&quot;,
                &quot;treeID&quot;: &quot;ST_AGP0N1600D&quot;,
                &quot;parentID&quot;: &quot;LIST_VC51010323468084_260&quot;,
                &quot;imgPath&quot;: &quot;./css/img/status_gray.gif&quot;,
                &quot;statusText&quot;: &quot;sph.status.fault&quot;,
                &quot;lastUpdateTimeText&quot;: &quot;2024-05-29 14:26:13&quot;,
                &quot;level&quot;: 4,
                &quot;children&quot;: null
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type   | Description                                |
|:---------------|:-------|:-------------------------------------------|
| serialNum      | string | Device SN                                  |
| lost           | string | Device online status (0: online, 1: offline) |
| status         | int    | Device status (0: offline, 1: online, 2: standby, 3: fault, other values indicate disconnection) |
| alias          | int    | Alias                                      |
| location       | string | Address                                    |
| dataLogSn      | string | Data logger serial number                  |
| nominalPower   | string | Rated power                                |
| power          | string | Current power                              |
| eToday         | string | Power generated today                      |
| eTotal         | string | Total power generated                      |
| lastUpdateTime | string | Last update time                           |
| tcpServerIp    | string | Server address                             |
| fwVersion      | string | Inverter firmware version                  |

**Notes**
- The retrieval frequency is once every 5 minutes or less.


---

# 35. The last detailed data of sph-s

*Page ID: `11292929836439932`*

  
**Brief Description:**

- Data format and parameter description of the last detailed data of the sph-s device

- `Only applicable to: Batch retrieval of the last data of the device.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;sph-s&quot;: [
            {
                &quot;serialNum&quot;: &quot;EFP0N1J023&quot;,
                &quot;dataLogSn&quot;: &quot;VC41010123438079&quot;,
                &quot;calendar&quot;: 1716965431997,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;ppv&quot;: 948.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 948.0,
                &quot;vpv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;vpv3&quot;: 349.5,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 2.7,
                &quot;pac&quot;: 888.0,
                &quot;fac&quot;: 49.98,
                &quot;vac1&quot;: 230.3,
                &quot;iac1&quot;: 1.3,
                &quot;pac1&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;eacToday&quot;: 8.1,
                &quot;eacTotal&quot;: 410.1,
                &quot;timeTotal&quot;: 0.0,
                &quot;epv1Today&quot;: 0.0,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 14.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epvToday&quot;: 14.0,
                &quot;epvTotal&quot;: 494.0,
                &quot;pf&quot;: -1.0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;systemFault&quot;: 0,
                &quot;systemWarn&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;deviceType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 6,
                &quot;sysFaultWord&quot;: 12337,
                &quot;sysFaultWord1&quot;: 12851,
                &quot;sysFaultWord2&quot;: 13365,
                &quot;sysFaultWord3&quot;: 13879,
                &quot;sysFaultWord4&quot;: 14393,
                &quot;sysFaultWord5&quot;: 16706,
                &quot;sysFaultWord6&quot;: 17220,
                &quot;sysFaultWord7&quot;: 17734,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 53.4,
                &quot;soc&quot;: 100,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridS&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadS&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 888.0,
                &quot;spStatus&quot;: 1,
                &quot;etoUserToday&quot;: 1.0,
                &quot;etoUserTotal&quot;: 535.8,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 6.4,
                &quot;edischarge1Today&quot;: 4.2,
                &quot;edischarge1Total&quot;: 172.7,
                &quot;echarge1Today&quot;: 9.5,
                &quot;echarge1Total&quot;: 177.9,
                &quot;elocalLoadToday&quot;: 9.7,
                &quot;elocalLoadTotal&quot;: 1018.2,
                &quot;upsFac&quot;: 50.0,
                &quot;upsVac1&quot;: 229.5,
                &quot;epsIac1&quot;: 3.8,
                &quot;upsPac1&quot;: 888.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;bmsSOC&quot;: 100,
                &quot;bmsBatteryVolt&quot;: 5.34,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 35.3,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 5.68,
                &quot;bmsUsingCap&quot;: 2000,
                &quot;pex&quot;: 888.0,
                &quot;esystemtoday&quot;: 18.200000762939453,
                &quot;esystemtotal&quot;: 666.7000122070312,
                &quot;eselftoday&quot;: 18.200000762939453,
                &quot;eselftotal&quot;: 660.2999877929688,
                &quot;psystem&quot;: 942.0,
                &quot;pself&quot;: 942.0,
                &quot;sysStatus&quot;: 3,
                &quot;dcTemp&quot;: 56.7,
                &quot;invTemp&quot;: 47.4,
                &quot;gridStatus&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;genVol&quot;: 0.0,
                &quot;genCurr&quot;: 0.0,
                &quot;genFreq&quot;: 0.0,
                &quot;genEnergy&quot;: 0.0,
                &quot;rLocalEnergy&quot;: 904.3,
                &quot;sLocalEnergy&quot;: 0.0,
                &quot;chipType&quot;: 0,
                &quot;genEnergyToday&quot;: 0.0,
                &quot;loadPower1&quot;: 760.0,
                &quot;loadPower2&quot;: 0.0,
                &quot;rLoadVol&quot;: 229.8,
                &quot;sLoadVol&quot;: 0.0,
                &quot;esystemHour&quot;: 0.7,
                &quot;esystemMonth&quot;: 328.9,
                &quot;esystemYear&quot;: 666.7,
                &quot;eselfHour&quot;: 0.7,
                &quot;eselfMonth&quot;: 323.2,
                &quot;eselfYear&quot;: 660.3,
                &quot;eToGridHour&quot;: 0.0,
                &quot;eToGridMonth&quot;: 5.7,
                &quot;eToGridYear&quot;: 6.4,
                &quot;eToUserHour&quot;: 0.0,
                &quot;eToUserMonth&quot;: 186.5,
                &quot;eToUserYear&quot;: 535.8,
                &quot;elocalLoadHour&quot;: 0.7,
                &quot;elocalLoadMonth&quot;: 509.7,
                &quot;elocalLoadYear&quot;: 1071.6,
                &quot;epvHour&quot;: 0.7,
                &quot;epvMonth&quot;: 256.6,
                &quot;epvYear&quot;: 494.0,
                &quot;batPower&quot;: 0.0,
                &quot;vbat1&quot;: 53.3,
                &quot;ibat&quot;: 0.0,
                &quot;m1Version&quot;: null,
                &quot;m2Version&quot;: null,
                &quot;hmiVersion&quot;: null,
                &quot;sphBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-05-29 14:50:31&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;statusText&quot;: &quot;Fault&quot;,
                &quot;again&quot;: false,
                &quot;ppvText&quot;: &quot;948.0 W&quot;,
                &quot;socText&quot;: &quot;100%&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-----  |:-----|----- |
| serialNum | String  | Serial Number |
| calendar  | Calendar  | Time |
| withTime  | boolean   | Whether the incoming data includes time |
| status | int | Min Status 0: waiting, 1: normal, 2: fault |
| isAgain | boolean  | Whether it is a retransmission |
| ppv  | double  | Total PV input power |
| ppv1 | double  | PV1 input power  |
| ppv2 | double  | PV2 input power  |
| ppv3 | double  | PV3 input power  |
| pac  | double  | Inverter output power  |
| pacToUserTotal | double | Total power flowing to the grid |
| pacToGridTotal | double | Total power flowing back from the grid |
| pacToLocalLoad | double | Total load power  |
| timeTotal | double | Total operating time  |
| epsPac   | float  | Off-grid output power  |
| vpv1 | float  | PV1 input voltage  |
| ipv1 | float  | PV1 input current  |
| vpv2 | float  | PV2 input voltage  |
| ipv2 | float  | PV2 input current  |
| vpv3 | float  | PV3 input voltage  |
| ipv3 | float  | PV3 input current  |
| fac  | float  | Grid frequency  |
| vac1 | float  | Grid voltage 1  |
| iac1 | float  | Grid current 1  |
| pac1 | float  | Inverter apparent power 1  |
| vac2 | float  | Grid voltage 2  |
| iac2 | float  | Grid current 2  |
| pac2 | float  | Inverter apparent power 2  |
| vac3 | float  | Grid voltage 3  |
| iac3 | float  | Grid current 3  |
| pac3 | float  | Inverter apparent power 3  |
| vacRs | float  | RS line voltage  |
| vacSt | float  | ST line voltage  |
| vacTr | float  | TR line voltage  |
| eacToday | float  | Inverter daily output energy  |
| eacTotal | double | Inverter total output energy  |
| epv1Today| float  | PV1 daily generated energy  |
| epv2Today| float  | PV2 daily generated energy  |
| epv3Today| float  | PV3 daily generated energy  |
| temp1 | float  | Temperature 1  |
| temp2 | float  | Temperature 2  |
| temp3 | float  | Temperature 3  |
| temp4 | float  | Temperature 4  |
| temp5 | float  | Temperature 5  |
| pBusVoltage   | float  | P Bus voltage  |
| nBusVoltage   | float  | N Bus voltage  |
| opFullwatt    | float  | Output power limit  |
| invDelayTime  | float  | Grid-tied inverter countdown  |
| pf   | float  | pf value  |
| epsPf | float  | Off-grid pf value  |
| dcVoltage    | float  | dc voltage  |
| epsFac  | float  | Off-grid frequency   |
| epsVac1 | float  | Off-grid R voltage  |
| epsIac1 | float  | Off-grid R current  |
| epsPac1 | float  | Off-grid R power  |
| epsVac2 | float  | Off-grid S voltage  |
| epsIac2 | float  | Off-grid S current  |
| epsPac2 | float  | Off-grid S power  |
| epsVac3 | float  | Off-grid T voltage  |
| epsIac3 | float  | Off-grid T current  |
| epsPac3 | float  | Off-grid T power  |
| dciR | float  | R phase DC current component  |
| dciS | float  | S phase DC current component  |
| dciT | float  | T phase DC current component  |
| sysFaultWord | int   | 1001  |
| sysFaultWord1 | int  | 1002  |
| sysFaultWord2 | int  | 1003  |
| sysFaultWord3 | int  | 1004  |
| sysFaultWord4 | int  | 1005  |
| sysFaultWord5 | int  | 1006  |
| sysFaultWord6 | int  | 1007  |
| sysFaultWord7 | int  | 1008  |
| faultType   | int  | Fault code  |
| warnCode    | int  | Warning code  |
| realOPPercent | int  | R   |
| deratingMode  | int  | Derating mode  |
| bdcStatus   | int  | BDC connection status  |
| dryContactStatus | int  | Dry contact connection status  |
| loadPercent  | int  | Off-grid load percentage  |
| uwSysWorkMode | int  | System working mode 1000  |
| gfci  | int  | Grid leakage current  |
| iso   | int  | PV insulation resistance  |
| etoUserToday | double  | Grid daily output energy  |
| etoUserTotal | double  | Grid total output energy  |
| etoGridToday | double  | Grid daily input energy  |
| etoGridTotal | double  | Grid total input energy  |
| elocalLoadToday | double  | User load daily consumption  |
| elocalLoadTotal | double  | User load total consumption  |
| epv1Total | double  | PV1 total generated energy  |
| epv2Total | double  | PV2 total generated energy  |
| epv3Total | double  | PV3 total generated energy  |
| epvTotal  | double  | Total PV generated energy  |
| echargeToday | double  | System daily charge energy  |
| echargeTotal | double  | System total charge energy  |
| edischargeToday | double  | System daily discharge energy  |
| edischargeTotal | double  | System total discharge energy  |
| eacChargeToday  | double  | AC daily charge energy  |
| eacChargeTotal  | double  | AC total charge energy  |
| BDC Parameters |  |  |
| bdc1Status	| int  | BDC1 status  |
| bdc1Mode		| int  | BDC1 mode  |
| bdc1FaultType | int  | BDC1 fault code  |
| bdc1WarnCode  | int  | BDC1 warning code  |
| bdc1Vbat		| float  | BDC1 battery voltage  |
| bdc1Ibat		| float  | BDC1 battery current   |
| bdc1Soc		| int  | BDC1 battery capacity  |
| bdc1Vbus1		| float  | BDC1 Bus1 voltage  |
| bdc1Vbus2		| float  | BDC1 Bus2 voltage  |
| bdc1Ibb		| float  | BDC1 BUCK-BOOST Current  |
| bdc1Illc		| float  | BDC1 LLC Current  |
| bdc1Temp1		| float  | BDC1 Temperature A  |
| bdc1Temp2		| float  | BDC1 Temperature B  |
| bdc1DischargePower | double  | BDC1 discharge power  |
| bdc1ChargePower | double  | BDC1 charge power  |
| bdc1DischargeTotal | double  | BDC1 total discharge energy  |
| bdc1ChargeTotal | double  | BDC1 total charge energy  |
| bdc2Status 	  | int  | BDC2 status  |
| bdc2Mode		  | int  | BDC2 mode  |
| bdc2FaultType	  | int  | BDC2 fault code  |
| bdc2WarnCode	  | int  | BDC2 warning code  |
| bdc2Vbat		  | float  | BDC2 battery voltage  |
| bdc2Ibat		  | float  | BDC2 battery current  |
| bdc2Soc		  | int  | BDC2 battery capacity  |
| bdc2Vbus1		  | float  | BDC2 Bus1 voltage  |
| bdc2Vbus2		  | float  | BDC2 Bus2 voltage  |
| bdc2Ibb		  | float  | BDC2 BUCK-BOOST Current  |
| bdc2Illc		  | float  | BDC2 LLC Current  |
| bdc2Temp1		  | float  | BDC2 Temperature A  |
| bdc2Temp2		  | float  | BDC2 Temperature B  |
| bdc2DischargePower | double  | BDC2 discharge power  |
| bdc2ChargePower | double  | BDC2 charge power  |
| bdc2DischargeTotal | double  | BDC2 total discharge energy  |
| bdc2ChargeTotal | double  | BDC2 total charge energy  |
| BMS Parameters |    |    |
| bmsStatus| int  | BMS status  |
| bmsFaultType| int  | BMS fault code  |
| bmsWarnCode| int  | BMS warning code   |
| bmsVbat| float  | BDC2 battery voltage  |
| bmsIbat| float  | BDC2 battery current  |
| bmsSoc| int  | BDC2 battery capacity  |
| bmsTemp1Bat| float  | BDC2 battery temperature  |
| bmsMaxCurr | float  | BDC2 maximum current   |
| bmsVdelta  | float  | BMS Delta voltage   |
| bmsIcycle | int  | BMS battery cycle count |
| bmsSoh | int  | BMS battery health index  |
| bmsCvVolt| float  | BMS lithium battery CV voltage |
| bmsInfo | float  | BMS information |
| bmsPackInfo | float  | BMS battery pack information |
| bmsUsingCap | float  | BMS battery capacity |
| bmsFwVersion | String  | BMS internal version |
| bmsMcuVersion | String  | BMS battery MCU version |
| bmsCommunicationType | int  | BMS communication type 0-RS485,1-CAN |

**Remarks** 
- The frequency of retrieval is once within every 5 minutes


---

# 36. Historical Data of sph-s Device

*Page ID: `11292930141133325`*

**Brief Description:**

- Data format and parameter description of sph-s device historical data
- `Applicable only to: obtain all detailed data of a specific device for a specific day.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-28&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;AGP0N1600D&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;calendar&quot;: 1716963973000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;ppv&quot;: 3855.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;vpv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;pac&quot;: 0.0,
                &quot;fac&quot;: 0.0,
                &quot;vac1&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;pac1&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;eacToday&quot;: 52.9,
                &quot;eacTotal&quot;: 10473.0,
                &quot;timeTotal&quot;: 0.0,
                &quot;epv1Today&quot;: 18.5,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 18.4,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 18.5,
                &quot;epv3Total&quot;: 0.0,
                &quot;epvToday&quot;: 55.4,
                &quot;epvTotal&quot;: 10758.6,
                &quot;pf&quot;: 0.0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;systemFault&quot;: 0,
                &quot;systemWarn&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;deviceType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 0,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 53.2,
                &quot;soc&quot;: 99,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridS&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadS&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 3734.0,
                &quot;spStatus&quot;: 0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 51.4,
                &quot;etoGridTotal&quot;: 10412.9,
                &quot;edischarge1Today&quot;: 0.0,
                &quot;edischarge1Total&quot;: 118.1,
                &quot;echarge1Today&quot;: 0.7,
                &quot;echarge1Total&quot;: 178.3,
                &quot;elocalLoadToday&quot;: 3.3,
                &quot;elocalLoadTotal&quot;: 285.5,
                &quot;upsFac&quot;: 50.0,
                &quot;upsVac1&quot;: 236.39999389648438,
                &quot;epsIac1&quot;: 0.0,
                &quot;upsPac1&quot;: 3734.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;bmsSOC&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0.0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;pex&quot;: 3738.0,
                &quot;esystemtoday&quot;: 55.400001525878906,
                &quot;esystemtotal&quot;: 10876.7001953125,
                &quot;eselftoday&quot;: 4.0,
                &quot;eselftotal&quot;: 463.79998779296875,
                &quot;psystem&quot;: 3855.0,
                &quot;pself&quot;: 3855.0,
                &quot;sysStatus&quot;: 3,
                &quot;dcTemp&quot;: 0.0,
                &quot;invTemp&quot;: 0.0,
                &quot;gridStatus&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;genVol&quot;: 0.0,
                &quot;genCurr&quot;: 0.0,
                &quot;genFreq&quot;: 0.0,
                &quot;genEnergy&quot;: 0.0,
                &quot;rLocalEnergy&quot;: 0.0,
                &quot;sLocalEnergy&quot;: 0.0,
                &quot;chipType&quot;: 0,
                &quot;genEnergyToday&quot;: 0.0,
                &quot;loadPower1&quot;: 3714.0,
                &quot;loadPower2&quot;: 0.0,
                &quot;rLoadVol&quot;: 0.0,
                &quot;sLoadVol&quot;: 0.0,
                &quot;esystemHour&quot;: 1.6,
                &quot;esystemMonth&quot;: 1943.5,
                &quot;esystemYear&quot;: 10876.7,
                &quot;eselfHour&quot;: 0.1,
                &quot;eselfMonth&quot;: 151.8,
                &quot;eselfYear&quot;: 463.8,
                &quot;eToGridHour&quot;: 1.5,
                &quot;eToGridMonth&quot;: 1791.7,
                &quot;eToGridYear&quot;: 10412.9,
                &quot;eToUserHour&quot;: 0.0,
                &quot;eToUserMonth&quot;: 0.0,
                &quot;eToUserYear&quot;: 0.0,
                &quot;elocalLoadHour&quot;: 0.1,
                &quot;elocalLoadMonth&quot;: 151.8,
                &quot;elocalLoadYear&quot;: 0.0,
                &quot;epvHour&quot;: 1.6,
                &quot;epvMonth&quot;: 1903.2,
                &quot;epvYear&quot;: 10758.6,
                &quot;batPower&quot;: 0.0,
                &quot;vbat1&quot;: 0.0,
                &quot;ibat&quot;: 0.0,
                &quot;m1Version&quot;: &quot;SK129.00-03141&quot;,
                &quot;m2Version&quot;: &quot;SK130.00-03131&quot;,
                &quot;hmiVersion&quot;: &quot;SK131.01-04301&quot;,
                &quot;sphBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Fault&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;ppvText&quot;: &quot;3855.0 W&quot;,
                &quot;socText&quot;: &quot;99%&quot;,
                &quot;time&quot;: &quot;2024-05-29 14:26:13&quot;
            },
			],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

 **Return Parameter Description**

| Parameter Name | Type | Description |
|:---------------|:-----|:------------|
| serialNum | String | Serial Number |
| calendar | Calendar | Time |
| withTime | boolean | Whether the incoming data includes a timestamp |
| status | int | Tlx Status 0: waiting, 1: normal, 2: fault |
| isAgain | boolean | Whether it is a retransmission |
| ppv | double | Total PV input power |
| ppv1 | double | PV1 input power |
| ppv2 | double | PV2 input power |
| ppv3 | double | PV3 input power |
| pac | double | Inverter output power |
| pacToUserTotal | double | Total power flowing to the grid |
| pacToGridTotal | double | Total power flowing from the grid |
| pacToLocalLoad | double | Total load power |
| timeTotal | double | Total running time |
| epsPac | float | Off-grid output power |
| vpv1 | float | PV1 input voltage |
| ipv1 | float | PV1 input current |
| vpv2 | float | PV2 input voltage |
| ipv2 | float | PV2 input current |
| vpv3 | float | PV3 input voltage |
| ipv3 | float | PV3 input current |
| fac | float | Grid frequency |
| vac1 | float | Grid voltage 1 |
| iac1 | float | Grid current 1 |
| pac1 | float | Inverter apparent power 1 |
| vac2 | float | Grid voltage 2 |
| iac2 | float | Grid current 2 |
| pac2 | float | Inverter apparent power 2 |
| vac3 | float | Grid voltage 3 |
| iac3 | float | Grid current 3 |
| pac3 | float | Inverter apparent power 3 |
| vacRs | float | RS line voltage |
| vacSt | float | ST line voltage |
| vacTr | float | TR line voltage |
| eacToday | float | Inverter daily output energy |
| eacTotal | double | Inverter total output energy |
| epv1Today | float | PV1 daily generation |
| epv2Today | float | PV2 daily generation |
| epv3Today | float | PV3 daily generation |
| temp1 | float | Temperature 1 |
| temp2 | float | Temperature 2 |
| temp3 | float | Temperature 3 |
| temp4 | float | Temperature 4 |
| temp5 | float | Temperature 5 |
| pBusVoltage | float | P Bus voltage |
| nBusVoltage | float | N Bus voltage |
| opFullwatt | float | Output power limit |
| invDelayTime | float | Grid-connected inverter countdown |
| pf | float | Power factor value |
| epsPf | float | Off-grid power factor value |
| dcVoltage | float | DC voltage |
| epsFac | float | Off-grid frequency |
| epsVac1 | float | Off-grid R voltage |
| epsIac1 | float | Off-grid R current |
| epsPac1 | float | Off-grid R power |
| epsVac2 | float | Off-grid S voltage |
| epsIac2 | float | Off-grid S current |
| epsPac2 | float | Off-grid S power |
| epsVac3 | float | Off-grid T voltage |
| epsIac3 | float | Off-grid T current |
| epsPac3 | float | Off-grid T power |
| dciR | float | R-phase DC current component |
| dciS | float | S-phase DC current component |
| dciT | float | T-phase DC current component |
| sysFaultWord | int | 1001 |
| sysFaultWord1 | int | 1002 |
| sysFaultWord2 | int | 1003 |
| sysFaultWord3 | int | 1004 |
| sysFaultWord4 | int | 1005 |
| sysFaultWord5 | int | 1006 |
| sysFaultWord6 | int | 1007 |
| sysFaultWord7 | int | 1008 |
| faultType | int | Fault code |
| warnCode | int | Warning code |
| realOPPercent | int | R |
| deratingMode | int | Derating mode |
| bdcStatus | int | BDC connection status |
| dryContactStatus | int | Dry contact connection status |
| loadPercent | int | Off-grid load percentage |
| uwSysWorkMode | int | System working mode 1000 |
| gfci | int | Grid leakage current |
| iso | int | PV insulation resistance |
| etoUserToday | double | Daily grid output energy |
| etoUserTotal | double | Total grid output energy |
| etoGridToday | double | Daily grid input energy |
| etoGridTotal | double | Total grid input energy |
| elocalLoadToday | double | User load daily consumption |
| elocalLoadTotal | double | User load total consumption |
| epv1Total | double | PV1 total generation |
| epv2Total | double | PV2 total generation |
| epv3Total | double | PV3 total generation |
| epvTotal | double | Total PV generation |
| echargeToday | double | System daily charging energy |
| echargeTotal | double | System total charging energy |
| edischargeToday | double | System daily discharging energy |
| edischargeTotal | double | System total discharging energy |
| eacChargeToday | double | AC daily charging energy |
| eacChargeTotal | double | AC total charging energy |
| BDC Parameters | | |
| bdc1Status | int | BDC1 status |
| bdc1Mode | int | BDC1 mode |
| bdc1FaultType | int | BDC1 fault code |
| bdc1WarnCode | int | BDC1 warning code |
| bdc1Vbat | float | BDC1 battery voltage |
| bdc1Ibat | float | BDC1 battery current |
| bdc1Soc | int | BDC1 battery capacity |
| bdc1Vbus1 | float | BDC1 Bus1 voltage |
| bdc1Vbus2 | float | BDC1 Bus2 voltage |
| bdc1Ibb | float | BDC1 BUCK-BOOST current |
| bdc1Illc | float | BDC1 LLC current |
| bdc1Temp1 | float | BDC1 temperature A |
| bdc1Temp2 | float | BDC1 temperature B |
| bdc1DischargePower | double | BDC1 discharging power |
| bdc1ChargePower | double | BDC1 charging power |
| bdc1DischargeTotal | double | BDC1 total discharging energy |
| bdc1ChargeTotal | double | BDC1 total charging energy |
| bdc2Status | int | BDC2 status |
| bdc2Mode | int | BDC2 mode |
| bdc2FaultType | int | BDC2 fault code |
| bdc2WarnCode | int | BDC2 warning code |
| bdc2Vbat | float | BDC2 battery voltage |
| bdc2Ibat | float | BDC2 battery current |
| bdc2Soc | int | BDC2 battery capacity |
| bdc2Vbus1 | float | BDC2 Bus1 voltage |
| bdc2Vbus2 | float | BDC2 Bus2 voltage |
| bdc2Ibb | float | BDC2 BUCK-BOOST current |
| bdc2Illc | float | BDC2 LLC current |
| bdc2Temp1 | float | BDC2 temperature A |
| bdc2Temp2 | float | BDC2 temperature B |
| bdc2DischargePower | double | BDC2 discharging power |
| bdc2ChargePower | double | BDC2 charging power |
| bdc2DischargeTotal | double | BDC2 total discharging energy |
| bdc2ChargeTotal | double | BDC2 total charging energy |
| BMS Parameters | | |
| bmsStatus | int | BMS status |
| bmsFaultType | int | BMS fault code |
| bmsWarnCode | int | BMS warning code |
| bmsVbat | float | BDC2 battery voltage |
| bmsIbat | float | BDC2 battery current |
| bmsSoc | int | BDC2 battery capacity |
| bmsTemp1Bat | float | BDC2 battery temperature |
| bmsMaxCurr | float | BDC2 maximum current |
| bmsVdelta | float | BMS Delta voltage |
| bmsIcycle | int | BMS battery cycle count |
| bmsSoh | int | BMS battery health index |
| bmsCvVolt | float | BMS lithium battery CV voltage |
| bmsInfo | float | BMS information |
| bmsPackInfo | float | BMS battery pack information |
| bmsUsingCap | float | BMS battery capacity |
| bmsFwVersion | String | BMS firmware version |
| bmsMcuVersion | String | BMS battery MCU version |
| bmsCommunicationType | int | BMS communication type 0-RS485, 1-CAN |

**Remarks**
- Data acquisition frequency is once every 5 minutes


---

# 37. Basic information about Noah

*Page ID: `11315140426110613`*

**Brief Description:**

- The data return format for basic information of Noah devices and the explanation of some parameters in the basic information
- `Only applicable for: Batch retrieval of basic information of devices.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;noah&quot;: [
            {
                &quot;deviceSn&quot;: &quot;0PVPOXIEGENGHUI1&quot;,
                &quot;datalogSn&quot;: &quot;0PVPOXIEGENGHUI1&quot;,
                &quot;associatedInvSn&quot;: null,
                &quot;portName&quot;: &quot;ShinePano-0PVPOXIEGENGHUI1&quot;,
                &quot;alias&quot;: null,
                &quot;location&quot;: null,
                &quot;lost&quot;: false,
                &quot;address&quot;: 1,
                &quot;lastUpdateTime&quot;: 1720667148000,
                &quot;sysTime&quot;: 1720660008000,
                &quot;status&quot;: 0,
                &quot;chargingSocHighLimit&quot;: 100,
                &quot;chargingSocLowLimit&quot;: 0,
                &quot;defaultPower&quot;: 200,
                &quot;componentPower&quot;: 0.0,
                &quot;time1Start&quot;: &quot;0:0&quot;,
                &quot;time1End&quot;: &quot;23:59&quot;,
                &quot;time1Mode&quot;: 0,
                &quot;time1Power&quot;: 400,
                &quot;time2Start&quot;: &quot;0:0&quot;,
                &quot;time2End&quot;: &quot;0:0&quot;,
                &quot;time2Mode&quot;: 0,
                &quot;time2Power&quot;: 200,
                &quot;time3Start&quot;: &quot;0:0&quot;,
                &quot;time3End&quot;: &quot;0:0&quot;,
                &quot;time3Mode&quot;: 0,
                &quot;time3Power&quot;: 200,
                &quot;time4Start&quot;: &quot;0:0&quot;,
                &quot;time4End&quot;: &quot;0:0&quot;,
                &quot;time4Mode&quot;: 0,
                &quot;time4Power&quot;: 200,
                &quot;time5Start&quot;: &quot;0:0&quot;,
                &quot;time5End&quot;: &quot;0:0&quot;,
                &quot;time5Mode&quot;: 0,
                &quot;time5Power&quot;: 200,
                &quot;time6Start&quot;: &quot;0:0&quot;,
                &quot;time6End&quot;: &quot;0:0&quot;,
                &quot;time6Mode&quot;: 0,
                &quot;time6Power&quot;: 200,
                &quot;time7Start&quot;: &quot;0:0&quot;,
                &quot;time7End&quot;: &quot;0:0&quot;,
                &quot;time7Mode&quot;: 0,
                &quot;time7Power&quot;: 200,
                &quot;time8Start&quot;: &quot;0:0&quot;,
                &quot;time8End&quot;: &quot;0:0&quot;,
                &quot;time8Mode&quot;: 0,
                &quot;time8Power&quot;: 200,
                &quot;time9Start&quot;: &quot;0:0&quot;,
                &quot;time9End&quot;: &quot;0:0&quot;,
                &quot;time9Mode&quot;: 0,
                &quot;time9Power&quot;: 200,
                &quot;time1Enable&quot;: 1,
                &quot;time2Enable&quot;: 0,
                &quot;time3Enable&quot;: 0,
                &quot;time4Enable&quot;: 0,
                &quot;time5Enable&quot;: 0,
                &quot;time6Enable&quot;: 0,
                &quot;time7Enable&quot;: 0,
                &quot;time8Enable&quot;: 0,
                &quot;time9Enable&quot;: 0,
                &quot;smartSocketPower&quot;: 0.0,
                &quot;otaDeviceTypeCodeHigh&quot;: &quot;PB&quot;,
                &quot;otaDeviceTypeCodeLow&quot;: &quot;FU&quot;,
                &quot;model&quot;: &quot;Noah 2000&quot;,
                &quot;fwVersion&quot;: null,
                &quot;mpptVersion&quot;: &quot;212004&quot;,
                &quot;pdVersion&quot;: &quot;211005&quot;,
                &quot;bmsVersion&quot;: &quot;213005&quot;,
                &quot;ebmOrderNum&quot;: 0,
                &quot;tempType&quot;: 0,
                &quot;lastUpdateTimeText&quot;: &quot;2024-07-11 11:05:48&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Explanation**

| Parameter Name         | Type      | Description                                |
|:-----------------------|:----------|:-------------------------------------------|
| deviceSn               | String    | Device Number                              |
| datalogSn              | String    | Data Logger Number                         |
| associatedInvSn        | String    | Associated Inverter                        |
| portName               | String    | Communication Port Name                    |
| alias                  | String    | Alias                                      |
| lost                   | Boolean   | Communication Lost                         |
| address                | Integer   | Inverter Address                           |
| lastUpdateTime         | Date      | Last Update Time                           |
| sysTime                | Date      | System Time                                |
| status                 | Integer   | 1: Normal;  4: Fault; 5: Heating           |
| chargingSocHighLimit   | Integer   | Charging SOC Upper Limit Register 0        |
| chargingSocLowLimit    | Integer   | Charging SOC Lower Limit                   |
| defaultPower           | Integer   | Default Micro-Inverter Output Power        |
| componentPower         | Double    | Component Power (W)                        |
| time1Start             | String    | Time Slot 1 Start                          |
| time1End               | String    | Time Slot 1 End                            |
| time1Mode              | Integer   | Time Slot 1 Mode                           |
| time1Power             | Integer   | Time Slot 1 Output Power Control           |
| time1Enable            | Integer   | Time Slot 1 Switch                         |
| time2Start             | String    | Time Slot 2 Start                          |
| time2End               | String    | Time Slot 2 End                            |
| time2Mode              | Integer   | Time Slot 2 Mode                           |
| time2Power             | Integer   | Time Slot 2 Output Power Control           |
| time2Enable            | Integer   | Time Slot 2 Switch                         |
| time3Start             | String    | Time Slot 3 Start                          |
| time3End               | String    | Time Slot 3 End                            |
| time3Mode              | Integer   | Time Slot 3 Mode                           |
| time3Power             | Integer   | Time Slot 3 Output Power Control           |
| time3Enable            | Integer   | Time Slot 3 Switch                         |
| time4Start             | String    | Time Slot 4 Start                          |
| time4End               | String    | Time Slot 4 End                            |
| time4Mode              | Integer   | Time Slot 4 Mode                           |
| time4Power             | Integer   | Time Slot 4 Output Power Control           |
| time4Enable            | Integer   | Time Slot 4 Switch                         |
| time5Start             | String    | Time Slot 5 Start                          |
| time5End               | String    | Time Slot 5 End                            |
| time5Mode              | Integer   | Time Slot 5 Mode                           |
| time5Power             | Integer   | Time Slot 5 Output Power Control           |
| time5Enable            | Integer   | Time Slot 5 Switch                         |
| time6Start             | String    | Time Slot 6 Start                          |
| time6End               | String    | Time Slot 6 End                            |
| time6Mode              | Integer   | Time Slot 6 Mode                           |
| time6Power             | Integer   | Time Slot 6 Output Power Control           |
| time6Enable            | Integer   | Time Slot 6 Switch                         |
| time7Start             | String    | Time Slot 7 Start                          |
| time7End               | String    | Time Slot 7 End                            |
| time7Mode              | Integer   | Time Slot 7 Mode                           |
| time7Power             | Integer   | Time Slot 7 Output Power Control           |
| time7Enable            | Integer   | Time Slot 7 Switch                         |
| time8Start             | String    | Time Slot 8 Start                          |
| time8End               | String    | Time Slot 8 End                            |
| time8Mode              | Integer   | Time Slot 8 Mode                           |
| time8Power             | Integer   | Time Slot 8 Output Power Control           |
| time8Enable            | Integer   | Time Slot 8 Switch                         |
| time9Start             | String    | Time Slot 9 Start                          |
| time9End               | String    | Time Slot 9 End                            |
| time9Mode              | Integer   | Time Slot 9 Mode                           |
| time9Power             | Integer   | Time Slot 9 Output Power Control           |
| time9Enable            | Integer   | Time Slot 9 Switch                         |
| smartSocketPower       | Double    | Smart Socket Power                         |
| otaDeviceTypeCodeHigh  | String    | OTA Device Type Code (High)                |
| model                  | String    | Model                                      |
| fwVersion              | String    | Hardware Version                           |
| mpptVersion            | String    | MPPT Version                               |
| pdVersion              | String    | PD Version                                 |
| bmsVersion             | String    | BMS Version                                |
| ebmOrderNum            | String    | Extended Battery Pack Serial Number        |
| tempType               | String    | Temperature Type                           |

**Remarks**
- Data retrieval frequency should be once every 5 minutes.

---

# 38. Noah latest detailed data.

*Page ID: `11315141402697236`*

**Brief Description:**

- Data format and parameter description of the last detailed data of the noah device

- `Only applicable for: Batch retrieval of the last data from devices.`

**Return Example**

``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;sph-s&quot;: [
            {
                &quot;serialNum&quot;: &quot;EFP0N1J023&quot;,
                &quot;dataLogSn&quot;: &quot;VC41010123438079&quot;,
                &quot;calendar&quot;: 1716965431997,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;ppv&quot;: 948.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 948.0,
                &quot;vpv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;vpv3&quot;: 349.5,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 2.7,
                &quot;pac&quot;: 888.0,
                &quot;fac&quot;: 49.98,
                &quot;vac1&quot;: 230.3,
                &quot;iac1&quot;: 1.3,
                &quot;pac1&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;eacToday&quot;: 8.1,
                &quot;eacTotal&quot;: 410.1,
                &quot;timeTotal&quot;: 0.0,
                &quot;epv1Today&quot;: 0.0,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 0.0,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 14.0,
                &quot;epv3Total&quot;: 0.0,
                &quot;epvToday&quot;: 14.0,
                &quot;epvTotal&quot;: 494.0,
                &quot;pf&quot;: -1.0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;systemFault&quot;: 0,
                &quot;systemWarn&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;deviceType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 6,
                &quot;sysFaultWord&quot;: 12337,
                &quot;sysFaultWord1&quot;: 12851,
                &quot;sysFaultWord2&quot;: 13365,
                &quot;sysFaultWord3&quot;: 13879,
                &quot;sysFaultWord4&quot;: 14393,
                &quot;sysFaultWord5&quot;: 16706,
                &quot;sysFaultWord6&quot;: 17220,
                &quot;sysFaultWord7&quot;: 17734,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 53.4,
                &quot;soc&quot;: 100,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridS&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadS&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 888.0,
                &quot;spStatus&quot;: 1,
                &quot;etoUserToday&quot;: 1.0,
                &quot;etoUserTotal&quot;: 535.8,
                &quot;etoGridToday&quot;: 0.0,
                &quot;etoGridTotal&quot;: 6.4,
                &quot;edischarge1Today&quot;: 4.2,
                &quot;edischarge1Total&quot;: 172.7,
                &quot;echarge1Today&quot;: 9.5,
                &quot;echarge1Total&quot;: 177.9,
                &quot;elocalLoadToday&quot;: 9.7,
                &quot;elocalLoadTotal&quot;: 1018.2,
                &quot;upsFac&quot;: 50.0,
                &quot;upsVac1&quot;: 229.5,
                &quot;epsIac1&quot;: 3.8,
                &quot;upsPac1&quot;: 888.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;bmsSOC&quot;: 100,
                &quot;bmsBatteryVolt&quot;: 5.34,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 35.3,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 5.68,
                &quot;bmsUsingCap&quot;: 2000,
                &quot;pex&quot;: 888.0,
                &quot;esystemtoday&quot;: 18.200000762939453,
                &quot;esystemtotal&quot;: 666.7000122070312,
                &quot;eselftoday&quot;: 18.200000762939453,
                &quot;eselftotal&quot;: 660.2999877929688,
                &quot;psystem&quot;: 942.0,
                &quot;pself&quot;: 942.0,
                &quot;sysStatus&quot;: 3,
                &quot;dcTemp&quot;: 56.7,
                &quot;invTemp&quot;: 47.4,
                &quot;gridStatus&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;genVol&quot;: 0.0,
                &quot;genCurr&quot;: 0.0,
                &quot;genFreq&quot;: 0.0,
                &quot;genEnergy&quot;: 0.0,
                &quot;rLocalEnergy&quot;: 904.3,
                &quot;sLocalEnergy&quot;: 0.0,
                &quot;chipType&quot;: 0,
                &quot;genEnergyToday&quot;: 0.0,
                &quot;loadPower1&quot;: 760.0,
                &quot;loadPower2&quot;: 0.0,
                &quot;rLoadVol&quot;: 229.8,
                &quot;sLoadVol&quot;: 0.0,
                &quot;esystemHour&quot;: 0.7,
                &quot;esystemMonth&quot;: 328.9,
                &quot;esystemYear&quot;: 666.7,
                &quot;eselfHour&quot;: 0.7,
                &quot;eselfMonth&quot;: 323.2,
                &quot;eselfYear&quot;: 660.3,
                &quot;eToGridHour&quot;: 0.0,
                &quot;eToGridMonth&quot;: 5.7,
                &quot;eToGridYear&quot;: 6.4,
                &quot;eToUserHour&quot;: 0.0,
                &quot;eToUserMonth&quot;: 186.5,
                &quot;eToUserYear&quot;: 535.8,
                &quot;elocalLoadHour&quot;: 0.7,
                &quot;elocalLoadMonth&quot;: 509.7,
                &quot;elocalLoadYear&quot;: 1071.6,
                &quot;epvHour&quot;: 0.7,
                &quot;epvMonth&quot;: 256.6,
                &quot;epvYear&quot;: 494.0,
                &quot;batPower&quot;: 0.0,
                &quot;vbat1&quot;: 53.3,
                &quot;ibat&quot;: 0.0,
                &quot;m1Version&quot;: null,
                &quot;m2Version&quot;: null,
                &quot;hmiVersion&quot;: null,
                &quot;sphBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;time&quot;: &quot;2024-05-29 14:50:31&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;statusText&quot;: &quot;Fault&quot;,
                &quot;again&quot;: false,
                &quot;ppvText&quot;: &quot;948.0 W&quot;,
                &quot;socText&quot;: &quot;100%&quot;
            }
        ]
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type   | Description |
|:---------------|:-------|-------------|
| deviceSn       | String | Device number |
| datalogSn      | String | Data logger serial number |
| time           | Date   | Time |
| isAgain        | Boolean| Whether it is retransmitted data |
| status         | Integer| 1: Normal, 4: Fault, 5: Heating |
| mpptProtectStatus | Integer | BIT0: PV1 overvoltage protection, BIT1: PV1 overcurrent protection, BIT2: PV1 overtemperature protection, BIT3: Reserved, BIT4: PV2 overvoltage protection, BIT5: PV2 overcurrent protection |
| pdWarnStatus   | Integer| BIT0: Communication with BMS failed, BIT1: Communication with MPPT failed |
| pac            | Double | BUCK output power |
| eacToday       | Double | Daily power generation |
| eacMonth       | Double | Monthly power generation |
| eacYear        | Double | Annual power generation |
| eacTotal       | Double | Total power generation |
| ppv            | Double | Photovoltaic power (W) |
| workMode       | Integer| Current time period working mode |
| totalBatteryPackChargingStatus | Integer | BIT0: Charging, BIT1: Discharging, if neither, display standby |
| totalBatteryPackChargingPower | Integer | Total battery charging/discharging power |
| batteryPackageQuantity | Integer | Number of parallel battery packs |
| totalBatteryPackSoc | Integer | Total battery pack SOC (State of Charge) percentage |
| heatingStatus  | Integer| Heating status, BIT0: Battery pack 1 is heating, BIT1: Battery pack 2 is heating, BIT2: Battery pack 3 is heating, BIT3: Battery pack 4 is heating |
| faultStatus    | Integer| Fault status, BIT0: Battery pack 1 fault, BIT1: Battery pack 2 fault, BIT2: Battery pack 3 fault, BIT3: Battery pack 4 fault |
| battery1SerialNum | String | Battery pack 1—SN |
| battery1Soc    | Integer| Battery pack 1_SOC |
| battery1Temp   | Double | Battery pack 1 temperature |
| battery1WarnStatus | Integer | Battery pack 1 warning status, BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Charging overcurrent warning, BIT7: Discharging overcurrent warning, BIT8~BIT15: Reserved |
| battery1ProtectStatus | Integer | Battery pack 1 protection status, BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Charging overcurrent protection, BIT7: Discharging overcurrent protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery2SerialNum | String | Battery pack 2—SN |
| battery2Soc    | Integer| Battery pack 2_SOC |
| battery2Temp   | Double | Battery pack 2 temperature |
| battery2WarnStatus | Integer | Battery pack 2 warning status, BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Charging overcurrent warning, BIT7: Discharging overcurrent warning, BIT8~BIT15: Reserved |
| battery2ProtectStatus | Integer | Battery pack 2 protection status, BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Charging overcurrent protection, BIT7: Discharging overcurrent protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery3SerialNum | String | Battery pack 3—SN |
| battery3Soc    | Integer| Battery pack 3_SOC |
| battery3Temp   | Double | Battery pack 3 temperature |
| battery3WarnStatus | Integer | Battery pack 3 warning status, BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Charging overcurrent warning, BIT7: Discharging overcurrent warning, BIT8~BIT15: Reserved |
| battery3ProtectStatus | Integer | Battery pack 3 protection status, BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Charging overcurrent protection, BIT7: Discharging overcurrent protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery4SerialNum | String | Battery pack 4—SN |
| battery4Soc    | Integer| Battery pack 4_SOC |
| battery4Temp   | Double | Battery pack 4 temperature |
| battery4WarnStatus | Integer | Battery pack 4 warning status, BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Charging overcurrent warning, BIT7: Discharging overcurrent warning, BIT8~BIT15: Reserved |
| battery4ProtectStatus | Integer | Battery pack 4 protection status, BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Charging overcurrent protection, BIT7: Discharging overcurrent protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |

**Notes**
- The frequency of acquisition is once per minute.


---

# 39. Noah Device Historical Data

*Page ID: `11315142054122408`*

**Brief Description:**

- Data format and parameter description of noah device historical data
- `Only applicable: for retrieving all detailed data of a specific device on a particular day.`

**Return Example**
``` 
{
    &quot;code&quot;: 0,
    &quot;data&quot;: {
        &quot;endDate&quot;: &quot;2024-05-28&quot;,
        &quot;datas&quot;: [
            {
                &quot;serialNum&quot;: &quot;AGP0N1600D&quot;,
                &quot;dataLogSn&quot;: null,
                &quot;calendar&quot;: 1716963973000,
                &quot;withTime&quot;: false,
                &quot;status&quot;: 6,
                &quot;lost&quot;: true,
                &quot;ppv&quot;: 3855.0,
                &quot;ppv1&quot;: 0.0,
                &quot;ppv2&quot;: 0.0,
                &quot;ppv3&quot;: 0.0,
                &quot;vpv1&quot;: 0.0,
                &quot;vpv2&quot;: 0.0,
                &quot;vpv3&quot;: 0.0,
                &quot;ipv1&quot;: 0.0,
                &quot;ipv2&quot;: 0.0,
                &quot;ipv3&quot;: 0.0,
                &quot;pac&quot;: 0.0,
                &quot;fac&quot;: 0.0,
                &quot;vac1&quot;: 0.0,
                &quot;iac1&quot;: 0.0,
                &quot;pac1&quot;: 0.0,
                &quot;vac2&quot;: 0.0,
                &quot;iac2&quot;: 0.0,
                &quot;pac2&quot;: 0.0,
                &quot;eacToday&quot;: 52.9,
                &quot;eacTotal&quot;: 10473.0,
                &quot;timeTotal&quot;: 0.0,
                &quot;epv1Today&quot;: 18.5,
                &quot;epv1Total&quot;: 0.0,
                &quot;epv2Today&quot;: 18.4,
                &quot;epv2Total&quot;: 0.0,
                &quot;epv3Today&quot;: 18.5,
                &quot;epv3Total&quot;: 0.0,
                &quot;epvToday&quot;: 55.4,
                &quot;epvTotal&quot;: 10758.6,
                &quot;pf&quot;: 0.0,
                &quot;faultCode&quot;: 0,
                &quot;faultBitCode&quot;: 0,
                &quot;systemFault&quot;: 0,
                &quot;systemWarn&quot;: 0,
                &quot;warnCode1&quot;: 0,
                &quot;warnCode&quot;: 0,
                &quot;priorityChoose&quot;: 0,
                &quot;deviceType&quot;: 0,
                &quot;uwSysWorkMode&quot;: 0,
                &quot;sysFaultWord&quot;: 0,
                &quot;sysFaultWord1&quot;: 0,
                &quot;sysFaultWord2&quot;: 0,
                &quot;sysFaultWord3&quot;: 0,
                &quot;sysFaultWord4&quot;: 0,
                &quot;sysFaultWord5&quot;: 0,
                &quot;sysFaultWord6&quot;: 0,
                &quot;sysFaultWord7&quot;: 0,
                &quot;pdischarge1&quot;: 0.0,
                &quot;pcharge1&quot;: 0.0,
                &quot;vbat&quot;: 53.2,
                &quot;soc&quot;: 99,
                &quot;pacToUserR&quot;: 0.0,
                &quot;pacToUserTotal&quot;: 0.0,
                &quot;pacToGridR&quot;: 0.0,
                &quot;pacToGridS&quot;: 0.0,
                &quot;pacToGridTotal&quot;: 0.0,
                &quot;plocalLoadR&quot;: 0.0,
                &quot;plocalLoadS&quot;: 0.0,
                &quot;plocalLoadTotal&quot;: 3734.0,
                &quot;spStatus&quot;: 0,
                &quot;etoUserToday&quot;: 0.0,
                &quot;etoUserTotal&quot;: 0.0,
                &quot;etoGridToday&quot;: 51.4,
                &quot;etoGridTotal&quot;: 10412.9,
                &quot;edischarge1Today&quot;: 0.0,
                &quot;edischarge1Total&quot;: 118.1,
                &quot;echarge1Today&quot;: 0.7,
                &quot;echarge1Total&quot;: 178.3,
                &quot;elocalLoadToday&quot;: 3.3,
                &quot;elocalLoadTotal&quot;: 285.5,
                &quot;upsFac&quot;: 50.0,
                &quot;upsVac1&quot;: 236.39999389648438,
                &quot;epsIac1&quot;: 0.0,
                &quot;upsPac1&quot;: 3734.0,
                &quot;epsVac2&quot;: 0.0,
                &quot;epsIac2&quot;: 0.0,
                &quot;upsPac2&quot;: 0.0,
                &quot;bmsSOC&quot;: 0,
                &quot;bmsBatteryVolt&quot;: 0.0,
                &quot;bmsBatteryCurr&quot;: 0.0,
                &quot;bmsBatteryTemp&quot;: 0.0,
                &quot;bmsSOH&quot;: 0,
                &quot;bmsConstantVolt&quot;: 0.0,
                &quot;bmsUsingCap&quot;: 0,
                &quot;pex&quot;: 3738.0,
                &quot;esystemtoday&quot;: 55.400001525878906,
                &quot;esystemtotal&quot;: 10876.7001953125,
                &quot;eselftoday&quot;: 4.0,
                &quot;eselftotal&quot;: 463.79998779296875,
                &quot;psystem&quot;: 3855.0,
                &quot;pself&quot;: 3855.0,
                &quot;sysStatus&quot;: 3,
                &quot;dcTemp&quot;: 0.0,
                &quot;invTemp&quot;: 0.0,
                &quot;gridStatus&quot;: 0,
                &quot;genPower&quot;: 0.0,
                &quot;genVol&quot;: 0.0,
                &quot;genCurr&quot;: 0.0,
                &quot;genFreq&quot;: 0.0,
                &quot;genEnergy&quot;: 0.0,
                &quot;rLocalEnergy&quot;: 0.0,
                &quot;sLocalEnergy&quot;: 0.0,
                &quot;chipType&quot;: 0,
                &quot;genEnergyToday&quot;: 0.0,
                &quot;loadPower1&quot;: 3714.0,
                &quot;loadPower2&quot;: 0.0,
                &quot;rLoadVol&quot;: 0.0,
                &quot;sLoadVol&quot;: 0.0,
                &quot;esystemHour&quot;: 1.6,
                &quot;esystemMonth&quot;: 1943.5,
                &quot;esystemYear&quot;: 10876.7,
                &quot;eselfHour&quot;: 0.1,
                &quot;eselfMonth&quot;: 151.8,
                &quot;eselfYear&quot;: 463.8,
                &quot;eToGridHour&quot;: 1.5,
                &quot;eToGridMonth&quot;: 1791.7,
                &quot;eToGridYear&quot;: 10412.9,
                &quot;eToUserHour&quot;: 0.0,
                &quot;eToUserMonth&quot;: 0.0,
                &quot;eToUserYear&quot;: 0.0,
                &quot;elocalLoadHour&quot;: 0.1,
                &quot;elocalLoadMonth&quot;: 151.8,
                &quot;elocalLoadYear&quot;: 0.0,
                &quot;epvHour&quot;: 1.6,
                &quot;epvMonth&quot;: 1903.2,
                &quot;epvYear&quot;: 10758.6,
                &quot;batPower&quot;: 0.0,
                &quot;vbat1&quot;: 0.0,
                &quot;ibat&quot;: 0.0,
                &quot;m1Version&quot;: &quot;SK129.00-03141&quot;,
                &quot;m2Version&quot;: &quot;SK130.00-03131&quot;,
                &quot;hmiVersion&quot;: &quot;SK131.01-04301&quot;,
                &quot;sphBean&quot;: null,
                &quot;dayMap&quot;: null,
                &quot;again&quot;: false,
                &quot;statusText&quot;: &quot;Fault&quot;,
                &quot;errorText&quot;: &quot;Unknown&quot;,
                &quot;warnText&quot;: &quot;Unknown&quot;,
                &quot;ppvText&quot;: &quot;3855.0 W&quot;,
                &quot;socText&quot;: &quot;99%&quot;,
                &quot;time&quot;: &quot;2024-05-29 14:26:13&quot;
            },
			],
        &quot;start&quot;: 0,
        &quot;haveNext&quot;: false
    },
    &quot;message&quot;: &quot;SUCCESSFUL_OPERATION&quot;
}
```

**Return Parameter Description**

| Parameter Name | Type | Description |
|:-----  |:-----|:----- |
| deviceSn | String | Device number |
| datalogSn | String | Data logger serial number |
| time | Date | Time |
| isAgain | Boolean | Is it retransmitted data |
| status | Integer | 1: Normal, 4: Fault, 5: Heating |
| mpptProtectStatus | Integer | BIT0: PV1 overvoltage protection, BIT1: PV1 overcurrent protection, BIT2: PV1 overtemperature protection, BIT3: Reserved, BIT4: PV2 overvoltage protection, BIT5: PV2 overcurrent protection |
| pdWarnStatus | Integer | BIT0: Communication with BMS failed, BIT1: Communication with MPPT failed |
| pac | Double | BUCK output power |
| eacToday | Double | Daily generated power |
| eacMonth | Double | Monthly generated power |
| eacYear | Double | Yearly generated power |
| eacTotal | Double | Total generated power |
| ppv | Double | Photovoltaic power (W) |
| workMode | Integer | Current time period work mode |
| totalBatteryPackChargingStatus | Integer | BIT0: Charging, BIT1: Discharging, if neither is present, standby is displayed |
| totalBatteryPackChargingPower | Integer | Total battery charging/discharging power |
| batteryPackageQuantity | Integer | Number of battery packs in parallel |
| totalBatteryPackSoc | Integer | Total battery pack SOC (State of Charge) as a percentage of battery capacity |
| heatingStatus | Integer | Heating status BIT0: Battery 1 is heating, BIT1: Battery 2 is heating, BIT2: Battery 3 is heating, BIT3: Battery 4 is heating |
| faultStatus | Integer | Fault status BIT0: Battery 1 fault, BIT1: Battery 2 fault, BIT2: Battery 3 fault, BIT3: Battery 4 fault |
| battery1SerialNum | String | Battery pack 1 - SN |
| battery1Soc | Integer | Battery pack 1 - SOC |
| battery1Temp | Double | Battery pack 1 - Temperature |
| battery1WarnStatus | Integer | Battery pack 1 warning status BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Overcurrent charging warning, BIT7: Overcurrent discharging warning, BIT8~BIT15: Reserved |
| battery1ProtectStatus | Integer | Battery pack 1 protection status BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Overcurrent charging protection, BIT7: Overcurrent discharging protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery2SerialNum | String | Battery pack 2 - SN |
| battery2Soc | Integer | Battery pack 2 - SOC |
| battery2Temp | Double | Battery pack 2 - Temperature |
| battery2WarnStatus | Integer | Battery pack 2 warning status BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Overcurrent charging warning, BIT7: Overcurrent discharging warning, BIT8~BIT15: Reserved |
| battery2ProtectStatus | Integer | Battery pack 2 protection status BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Overcurrent charging protection, BIT7: Overcurrent discharging protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery3SerialNum | String | Battery pack 3 - SN |
| battery3Soc | Integer | Battery pack 3 - SOC |
| battery3Temp | Double | Battery pack 3 - Temperature |
| battery3WarnStatus | Integer | Battery pack 3 warning status BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Overcurrent charging warning, BIT7: Overcurrent discharging warning, BIT8~BIT15: Reserved |
| battery3ProtectStatus | Integer | Battery pack 3 protection status BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Overcurrent charging protection, BIT7: Overcurrent discharging protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |
| battery4SerialNum | String | Battery pack 4 - SN |
| battery4Soc | Integer | Battery pack 4 - SOC |
| battery4Temp | Double | Battery pack 4 - Temperature |
| battery4WarnStatus | Integer | Battery pack 4 warning status BIT0: Low voltage warning, BIT1: High voltage warning, BIT2: Low charging temperature warning, BIT3: High charging temperature warning, BIT4: Low discharging temperature warning, BIT5: High discharging temperature warning, BIT6: Overcurrent charging warning, BIT7: Overcurrent discharging warning, BIT8~BIT15: Reserved |
| battery4ProtectStatus | Integer | Battery pack 4 protection status BIT0: Low voltage protection, BIT1: High voltage protection, BIT2: Low charging temperature protection, BIT3: High charging temperature protection, BIT4: Low discharging temperature protection, BIT5: High discharging temperature protection, BIT6: Overcurrent charging protection, BIT7: Overcurrent discharging protection, BIT8: Battery error, BIT9: NTC disconnection, BIT10: Voltage sampling line disconnection, BIT11~BIT15: Reserved |

**Remarks**
- Frequency of collection is once every 5 minutes or less.


---

# 40. Set the power on and off

*Page ID: `11330750679726415`*



**Brief Description:** 

- Set the active power percentage of the device based on the device type and SN of the device, and the data returned by the interface only returns the device setting result for which the key token has permission to access, and the device without permission will not be set and will not return the result


- `Device type is the deviceType parameter in the interface for obtaining device list.`
- `Noah type devices do not support power on/off settings`
- `Current interface frequency is once every 5 seconds`

**Request URL:** 

- ` http(s)://openapi.growatt.com/v4/new-api/setOnOrOff`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded

Http Header Parameters and Description:

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|
|value |yes |int| 0: Shut down, 1: Turn on|

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;,
&quot;value&quot;: &quot;25&quot;

}
```
 **Example of Return**
 
The setup was successful
 ```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_SUCCESSFUL&quot;
}
```

---

# 41. Set the active power

*Page ID: `11330751643769012`*


**Brief Description:** 

- Set the active power percentage of the device based on the device type and SN of the device, and the data returned by the interface only returns the device setting result for which the key token has permission to access, and the device without permission will not be set and will not return the result
- 'Device Type' is the deviceType parameter in the API for obtaining the device list. `
- 'Current interface frequency 5S once'

**Request URL:** 
- ` http(s)://openapi.growatt.com/v4/new-api/setPower`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded 

Http Header Parameters and Description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|
|value |yes |int |Percentage of active power, range 0-100, example: 25. Note: NOAH device type is set to power (range 0-800W, unit W)|

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;,
&quot;value&quot;: &quot;25&quot;

}
```
 **Example of Return**
 
The setup was successful
 ```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_SUCCESSFUL&quot;
}
```

---

# 42. Set the upper limit of the discharge SOC

*Page ID: `11330751904512654`*


**Brief Description:** 

- Set the upper limit of the discharge SOC of the device based on the device type noah and the SN of the device, and the data returned by the interface only returns the device setting result for which the key token has permission to access, and the device without permission will not be set and will not return the result
- 'Device Type' is the deviceType parameter in the API for obtaining the device list. `
- 'Current interface frequency 5S once'
- Note: Currently, only the upper limit of the discharge SOC of the noah device type machine is supported. `

**Request URL:** 
- ` http(s)://openapi.growatt.com/v4/new-api/setHighLimitSoc`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded 

Http Header Parameters and Description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string  |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|
|value |yes |int |discharge SOC limit, range 0-100, example: 25. Note: This API is only applicable to NOAH device type |

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;,
&quot;value&quot;: &quot;25&quot;

}
```
 **Example of Return**
 
The setup was successful
 ```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_SUCCESSFUL&quot;
}
```
  

---

# 43. Set the lower discharge SOC limit

*Page ID: `11330752473301776`*

  
**Brief Description:** 

- Set the lower discharge SOC limit of the device based on the device type noah and the SN of the device, and the data returned by the interface only returns the device setting result for which the key token has permission to access, and the device without permission will not be set and will not return the result
- 'Device Type' is the deviceType parameter in the API for obtaining the device list. `
- 'Current interface frequency 5S once'
- Note: Currently, only the lower discharge SOC limit for noah device type machines is supported. `

**Request URL:** 
- ` http(s)://openapi.growatt.com/v4/new-api/setLowLimitSoc`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded 

Http Header Parameters and Description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|
|value |yes |int |discharge SOC lower limit, range 0-100, example: 25. Note: This API is only applicable to NOAH device types (the lower limit cannot exceed the upper limit).

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;,
&quot;value&quot;: &quot;25&quot;

}
```
 **Example of Return**
 
The setup was successful
```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_SUCCESSFUL&quot;
}

```

---

# 44. Set the time period and mode

*Page ID: `11330752683972660`*


**Brief Description:** 

- Set the time period and machine mode of the device based on the device type noah and the SN of the device, and the data returned by the interface only returns the device setting result that the key token has permission to access, and the device without permission will not be set and will not return the result
- 'Device Type' is the deviceType parameter in the API for obtaining the device list. `
- 'Current interface frequency 5S once'
- Note: Currently, only the time period and machine mode settings of the NOAH device type machine are supported. `

**Request URL:** 
- ` http(s)://openapi.growatt.com/v4/new-api/setTimeSegment`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded 

Http Header Parameters and Description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string  |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|
|type |yes |string |time period (1~9), example: 1 |
|startTime |yes |string |start time (hours:minutes), Example: 01:06 |
|endTime |yes |string |end time (hours:minutes), Example: 02:05 |
|mode |yes |string |machine mode (0: load priority, 1: battery priority), example: 0 |
|power | is |string |output power (range 0-800 in w), example: 150 |
|enable |yes |string |time period switch (0: off, 1: on), example: 0|

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;,
&quot;startTime&quot;: &quot;01:06&quot;,
&quot;endTime&quot;: &quot;02:05&quot;,
&quot;mode&quot;: &quot;0&quot;,
&quot;power&quot;: &quot;150&quot;,
&quot;enable&quot;: &quot;0&quot;

}
```
 **Example of Return**
succeed
 ```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_SUCCESSFUL&quot;
}
```

Permission denied No token specified or token exception
```
{
    &quot;code&quot;: 101,
    &quot;message&quot;: &quot;PERMISSION_DENIED&quot;
}
```
Failed to set the parameters
```
{
    &quot;code&quot;: 6,
    &quot;data&quot;: null,
    &quot;message&quot;: &quot;PARAMETER_SETTING_FAILED&quot;
}
```


---

# 45. Read power

*Page ID: `11558661372387309`*


**Brief Description:** 

- Set the active power percentage of the device based on the device type and SN of the device, and the data returned by the interface only returns the device setting result for which the key token has permission to access, and the device without permission will not be set and will not return the result
- &#039;Device Type&#039; is the deviceType parameter in the API for obtaining the device list. `
- &#039;Current interface frequency 5S once&#039;

**Request URL:** 
- ` http(s)://openapi.growatt.com/v4/new-api/readPower`
  
**Request method:**
- POST 

**Content-Type：**
- application/x-www-form-urlencoded 

Http Header Parameters and Description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|token |Yes|String |keytoken|

Http body parameters and description: 

|Parameter Name|Required|Type|Description|
|:----    |:---|:----- |-----   |
|deviceSn |is |string |device SN, example: xxxxxxx |
|deviceType |yes |string |[Equipment type](https://www.showdoc.com.cn/p/e9f6e73f251e6364fe1d43e9d4cc1eec &quot;Equipment type&quot;)|

**Call Example**

```
{
&quot;deviceSn&quot;: &quot;FDCJQ00003&quot;,
&quot;deviceType&quot;: &quot;noah&quot;

}
```
 **Example of Return**
 
The setup was successful
 ```
 {
    &quot;code&quot;: 0,
    &quot;data&quot;: 40,
    &quot;message&quot;: &quot;success&quot;
}
```


---

