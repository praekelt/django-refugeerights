Snappy CSV Upload Format
=================================================

In order to upload FAQs to Snappy using the provided uploaded in admin,
the files need to formatted correctly, such as the example below. ::
  lang,topic,question,answer
  en,When/where to apply,Apply at RRO,"Apply immediately after you arrive by visiting a Refugee Reception Office (RRO). If an officer questions you before that, you must say you are going to apply."
  en,When/where to apply,Durban,"Your nearest Refugee Reception Office (RRO) in Durban is situated at 132 Moore Street, Durban. Call them on 031-362-1205 or fax on 031-362-1220."
  en,When/where to apply,Musina,"Your nearest Refugee Reception Office (RRO) in Musina is situated at 8 Harold Street (next to the post office). Tel: 015-534-5300; Fax: 015-534-5332."
  en,Appl. Results,Successful,"If your application is approved, you'll get a Section 24 permit (refugee status). Your permit is valid for 2 to 4 years. You must renew it at your RRO before it expires. Refugees can apply for a refugee ID (maroon ‘ID') and travel documents. It may take time. Only apply for travel documents if you have a refugee ID. If you don't, and must travel for an emergency, contact UNHCR. Tip: If you travel back to your country, you could lose your refugee status in SA."
  en,Appl. Results,Unsuccessful,"If a RRO rejects your application, you're not recognised as a refugee. You have 30 days to give a notice of appeal, otherwise you must document your stay in another way or leave SA. The reason for rejection affects your appeal. If your application. was fraudulent or abusive, the Standing Committee of Refugee Affairs will review it. You have 14 days to give them a written statement on why you disagree, at the RRO that issued the rejection letter. Ask a LHR counsellor for help."

The first line must contain all the column headers in order to identify which
column is which. Each of the following lines specifies a question in the FAQ.
In Snappy, topics belong to a particular FAQ. The above example would add
2 topics and 5 questions. For example if the FAQ name was *Step1: Applying for Asylum*,
the example would produce the following structure:
  1. Step1: Applying for Asylum

    a. [en] When/where to apply

      * [en] Apply at RRO

        * Answer

      * [en] Durban

        * Answer

      * [en] Musina

        * Answer

    b. [en]Appl. Results

      * [en] Successful

        * Answer

      * [en] Unsuccessful

        * Answer

.. warning::

   Make sure to surround any entries which contain commas with quotes (ie. "Testing, Testing, Testing.").
