# SDLENS: Getting Started

## 1: Starting SDLENS.

**i. OPTIONAL**: Create a virtual environment so that python packages are not installed directly onto your machine.


**ii**. In the directory where the application is located make sure that you have all of the neccicary requirements. This can be accomplished with the following command, and the use of the `requirements.txt` package file.

```sh
$ pip3 install -r "requirements.txt"
```

**iii**. The application is now ready to start, and to do so, use the following command from the root directory:

```sh
./startup.py
```

**iv**. You will be asked a few options:
```sh
Keep exising credentials file? [Y/n]:
Do you want to change any values [Y/n]:
Does the database exist [Y/n]:
Does the database need to be cleared [Y/n]:
```

**Optionally, you could run the webapp and agent processes individually:**

Agent process used to update the database:
```sh
python3 agent/
```

Front end webapp:
```sh
webapp/app.py
```

**v**. The application should now be fully opperational.

## 2: Logging In

First off, before you can proceed with using SDLENS, you need to login. You will be redirected to this page if you are not already authentiated. 
![Login_page](https://user-images.githubusercontent.com/44167644/55676306-99366000-58a0-11e9-8c69-33eede899e4f.png)

However, if you would like to register a new user (which you will be required to if it is your first time), it can be done from the register user page pictured below:
![Register Page](https://user-images.githubusercontent.com/44167644/55676319-0e099a00-58a1-11e9-8666-8cc9d3a69064.png)

Once logged in you will be brought to the SDLens Dashboard!
![dashboard](https://user-images.githubusercontent.com/44167644/55676744-c25aee80-58a8-11e9-87b4-ef181389d8a9.png)

**Please view the Owners_manual.md file for additional information.**